#13F scraper

#http://www.sec.gov/cgi-bin/browse-edgar?CIK=0001167483&action=getcompany&type=13f
#cik: is the firm identification number
#action: needs to equal getcompany
#type: 13f narrows it down
#http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&
	#CIK=0001167483&type=13f&start=0&count=40&output=atom
#this is the RSS feed
#provides the filing-date and filing-href

#search for *** for $$$ for things to work on within the code

from lxml import etree, html

import MySQLdb
import requests
#import lxml
from contextlib import closing
import datetime
#import xml.etree.cElementTree as ET
import keys
import logging

#Errors
#********Must deal with ammended 13Fs, 53417 in particular. looking at it, not only is it pulling 13fs incorrectly, it's marking them as 
#an incorrect date

#**************Files were submitted as text files prior to 3Q13...shit
#************Standardize uses of .format vs %s
#******** Need to pull the acceptd date
#*********When a new report is found the analyze class needs to be called
#******need to try/except all url calls 
#***********Need to implement logging
#**********Deal with Empty Ticker CUSIPs


#Notes
#Don't need zeros in front of CIK and should take those out at the initial upload level

#This class will check for the most recent form 
class UpdateChecker(object):

	#********checks database for most recent 13F and returns the last date
	#********checks to see whether or not a 13F should even be available
	#********will return the last date, this date will eventually be used to call get13FList
	#**** maybe this should be its own class that will track if and when a 13F needs to be checked
	#for, then the get13FList and cleanEntryElement classes could be it's own class
	def mostRecentForm13F(self, cik):
		db = MySQLdb.connect(host = keys.sqlHost, user = keys.sqlUsername, passwd = keys.sqlPassword, db="Quarterly13Fs") 
		with closing(db.cursor()) as cur:
			cur.execute("SELECT MAX(filingDate) FROM 13FList WHERE CIK=%s" %(cik))
			lastDate = cur.fetchone()[0]
		db.close()
		return lastDate

	#********check the dates i have and which i should upload
	#********check whether there are 40 lists, if so i need to run again
	def get13FList(self, cik, lastDate = None):
		rssListString = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%s&type=13f-hr&start=0&count=40&output=atom" % (cik)
		page = requests.get(rssListString)
		tree = etree.fromstring(page.content)
		namespace = "{%s}" % (tree.nsmap[None])
		entryElements = tree.findall('{0}entry'.format(namespace))
		entries = self.cleanEntryElements(entryElements, namespace, lastDate)
		#entries is a list of lists.  list has accessionNunber and date	
		return entries

	def cleanEntryElements(self, entryElements, namespace, lastDate):
		entries = []
		for entry in entryElements:
			#yes it is nunber
			#get and clean accession from "-"
			filingDate = entry.find('{0}content/{0}filing-date'.format(namespace)).text
			#converst filingDate to a date format so it can be compared to the last date in date format
			filingTime = datetime.datetime.strptime(filingDate, "%Y-%m-%d").date()
			#only hits the if when the lastDate available is bigger than the filing date
			#this if statement assumes that the RSS feed is in chronlogical order top to bottom
			if (lastDate is not None and filingTime <= lastDate):
				#print filingDate
				return entries
			accessionNunber = entry.find('{0}content/{0}accession-nunber'.format(namespace)).text.replace("-","")
			entries.append([accessionNunber,filingDate])
		return entries

#This class is intialized with a cik (the firm id), and entries (which is a 2d list of the accession nunbers
# the date) It takes this cik and Accession Nunbers (13F IDs), parses them, the uploads them to the
#database
class Form13FUpdater(object):
	#initializes class with the CIK and a 2d list called entires
	#the CIK is the identification number of the Firm
	#entries is a list containing lists of as accessionNunbers and filing dates 
	def __init__(self, cik, entries):
		self.cik = cik
		self.entries = entries

	#entryParser goes through the entry list, and calls scrapeForm13F which returns infoTables
	#it then passes infoTables to upload13FHoldings
	def entryParser(self):
		print "cik: %s" %(self.cik)
		failCount = 0
		for entry in self.entries:
			accessionNunber = entry[0]
			filingDate = entry[1]
			if failCount <= 3:
				print "Working on accessionNunber: %s, and filingDate: %s" %(accessionNunber, filingDate)
				infoTables = self.scrapeForm13F(accessionNunber)
			else:
				print "Skipped accessionNunber: %s, and filingDate: %s" %(accessionNunber, filingDate)
			#the only reason it wouldn't be info tables is if the http request is not 200
			if infoTables:
				#uploads the holdings into the database, the form info to 13FList
				print "Uploading accessionNunber: %s, and filingDate: %s" %(accessionNunber, filingDate)
				self.upload13FHoldings(accessionNunber, filingDate, infoTables)
				failCount = 0
			else:
				failCount +=1
				#***********Should take this opportunity to update CUSIP Database 
				#Maybe in the process can implement fuzzywuzzy library when looking up cusip and tickers


	#scrapeForm13F takes the accessionNunber as an argurment then downloads an xml with the 
	#data. And puts all of the "infoTables" from the file into a list called infoTableElements
	#it then calls cleanInfoTableElements which returns a cleaned infoTables
	#this function returns infoTables
	def scrapeForm13F(self, accessionNunber):
		#*********Some sort of smart selection to use the xmlName that worked last time
		#xmlNames = ("infotable", "form13fInfoTable", "Form13fInfoTable")

		xmlName = self.getInformationTableName(accessionNunber)
		#*********if xml name doesn't exist i.e. if there are only text files...
		if not xmlName:
			return

		xmlURLString = "http://www.sec.gov/Archives/edgar/data/{0}/{1}/{2}.xml".format(self.cik, accessionNunber, xmlName)
		page = requests.get(xmlURLString)
		#checks if page returns
		if page.status_code == 200:
			tree = etree.fromstring(page.content)
			#so namespace is found using the nsmap fuction.  nsmap returns a dictionary, normally
			#of one pair with a key of None, but sometimes a single pair wih key of n1, and sometimes
			#multiple pairs
			namespace = None
			if None in tree.nsmap:
				namespace = "{%s}" %(tree.nsmap[None])
			else:
				for val in tree.nsmap.values():
					#assumes that the namespace will be the http://....
					if val.startswith("http://www.sec.gov"):
						namespace = "{%s}" %(val)

			#namespace = "{%s}" % (tree.nsmap.values()[0])
			#namespace = "{%s}" % (tree.nsmap[None])
			infoTableElements = tree.findall('{0}infoTable'.format(namespace))
			infoTables = self.cleanInfoTableElements(infoTableElements, namespace)
			#print infoTables
			return infoTables
		else:
			#*******ACTUALLY CATCH THIS ERROR
			#********can do a text scraping here...
			print "FAIL FAIL FAIL"
			return 

	#gets the name of the XML used by the SEC, this is not standardized for some reason
	def getInformationTableName(self, accessionNunber):
		pageURLString = "http://www.sec.gov/Archives/edgar/data/%s/%s-%s-%s-index.htm" % (self.cik, accessionNunber[0:10], accessionNunber[10:12], accessionNunber[12:])
		#print pageURLString
		parser = etree.HTMLParser()
		tree = etree.parse(pageURLString, parser)

		#finds all the names and the descriptions
		informationTableNames = tree.xpath('//*[@id="formDiv"]//*/tr/td[3]/a/text()')
		typeNames = tree.xpath('//*[@id="formDiv"]//*/tr/td[4]/text()')

		SEARCH_NAME = "INFORMATION TABLE"
		#looks for the description of SEARCH_NAME then returns the name of the document
		if SEARCH_NAME in typeNames:
			longInformationTableName = informationTableNames[typeNames.index(SEARCH_NAME)]
			informationTableName = longInformationTableName[0:longInformationTableName.rfind('.')]
			return informationTableName
		else:
			return None


	#clean InfoTableElements takes infoTableElements and the namespace of the xml as 
	#parameters.  The xml names are defined within this section in the keys
	#dictionary.  The Function then loops through the infoTableElements and pulls out the
	#data and stores it in an infoDict.  the infoDict is then stored in infoTables and
	#returned
	#returns infoTables, a list of dictionaries 
	def cleanInfoTableElements(self, infoTableElements, namespace):
		infoTables = []
		keys = {
				'nameOfIssuer': '{0}nameOfIssuer',
				'titleOfClass': '{0}titleOfClass',
				'cusip': '{0}cusip',
				'value': '{0}value',
				'sshPrnamt': '{0}shrsOrPrnAmt/{0}sshPrnamt',
				'sshPrnamtType': '{0}shrsOrPrnAmt/{0}sshPrnamtType',
				'putCall': '{0}putCall',
				'investmentDiscretion': '{0}investmentDiscretion',
				'Sole': '{0}votingAuthority/{0}Sole',
				'Shared': '{0}votingAuthority/{0}Shared',
				'None': '{0}votingAuthority/{0}None'
			}
		for infoTable in infoTableElements:
			infoDict = {}
			#$$$this is technical a third nested for loop, but i don't believe there is a more efficent
			#way to do this as I need all of the information this is looping through (complete matrix)
			for key, path in keys.iteritems():
				#this if is for the "putcall" tag as not all infoTables have this
				if (infoTable.find(path.format(namespace))) is not None:
					infoDict[key] = infoTable.find(path.format(namespace)).text	
				#should put in "n/a" for putcall if it is empty
				else:
					infoDict[key] = 'n/a'
			infoTables.append(infoDict)
			
		return infoTables

	def upload13FHoldings(self, accessionNunber, filingDate, infoTables):
		db = MySQLdb.connect(host="127.0.0.1",user = keys.sqlUsername, passwd = keys.sqlPassword, db="Quarterly13Fs") 

		#load the data into 13FHoldings and if successful then add to the 13FList database

		with closing(db.cursor()) as cur:
			#belt and suspenders check here to see if the accessionNunber is already in
			#the 13FHolding Database and if it is don't do shit
			cur.execute("SELECT COUNT(*) as count FROM 13FHoldings WHERE accessionNunber = %s" %(accessionNunber))
			existingEntries = cur.fetchone()[0]

			if existingEntries < len(infoTables):
				for iT in infoTables:
					cur.execute("INSERT INTO 13FHoldings (accessionNunber, nameOfIssuer, titleOfClass, cusip, \
						value, sshPrnamt, sshPrnamtType, putCall, investmentDiscretion, Sole, Shared, None) \
						VALUES ('%s', '%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s')" 
						% (accessionNunber, iT['nameOfIssuer'].replace("'","''")[0:95], iT['titleOfClass'].replace("'","''"), 
							iT['cusip'], iT['value'],iT['sshPrnamt'], iT['sshPrnamtType'], iT['putCall'], 
							iT['investmentDiscretion'], iT['Sole'], iT['Shared'],iT['None']))

					#this little nibblet checks the CUSIPList table and updates it if there is a 
					#cusip that I don't know
					cur.execute("SELECT Ticker FROM CUSIPList WHERE CUSIP = '%s'" %(iT['cusip']))
					if not cur.fetchone():
						tickerPair = self.tickerLookup(iT['cusip'])
						if tickerPair:
							cur.execute("INSERT INTO CUSIPList (CUSIP, Ticker, LongName)\
								VALUES ('%s','%s','%s')" % (iT['cusip'], tickerPair[0], tickerPair[1]))
						#this else is if the lookup on fidelity quotes fails, puts only cusip in if 
						else:
							cur.execute("INSERT INTO missingCUSIP (CUSIP, accessionNunber)\
								VALUES ('%s', '%s')" % (iT['cusip'], accessionNunber))

				#makes date object
				filingTime = datetime.datetime.strptime(filingDate, "%Y-%m-%d").date()
				#calculates quarter end
				quarterDate = self.calculateQuarterDate(filingTime)

				cur.execute("INSERT INTO 13FList (CIK, filingDate, quarterDate, accessionNunber) \
					VALUES('%s', '%s', '%s','%s')"
					%(self.cik, filingTime, quarterDate, accessionNunber))

				db.commit()

			else:
				#****Should log some error here if gets to this point and it has somethings in database already
				pass
		db.close()	

	#*******This is fundamentally incorrect, should pull actual date
	def calculateQuarterDate(self, filingTime):
		quarterYear = None
		quarterMonth = None
		quarterDay = None
		if filingTime.month < 3:
			quarterYear = filingTime.year - 1
			quarterMonth = 12
		else: 
			quarterYear = filingTime.year
			quarterMonth = filingTime.month - (filingTime.month % 3)
		if quarterMonth == 3 or quarterMonth == 12:
			quarterDay = 31
		else:
			quarterDay = 30
		return datetime.date(quarterYear, quarterMonth, quarterDay)

	#***********NEEEDDD TO DO SOME ERROR CATCHING HERE
	def tickerLookup(self, cusip):
		#baseURL = "http://activequote.fidelity.com/mmnet/SymLookup.phtml?reqforlookup=REQUESTFORLOOKUP&for=stock&by=cusip&criteria=%s" %(cusip)
		baseURL = "http://quotes.fidelity.com/mmnet/SymLookup.phtml?reqforlookup=REQUESTFORLOOKUP&productid=mmnet&isLoggedIn=mmnet&rows=50&for=stock&by=cusip&criteria=%s&submit=Search" % (cusip)
		parser = etree.HTMLParser()
		#******Before trying check to see if CUSIP is in the missingCUSIP db
		try:
			tree = etree.parse(baseURL, parser)
			#finds all the names and the descriptions
			longName = tree.xpath('//*/tr[3]/td[1]/font/text()')[0]
			ticker = tree.xpath('//*/tr[3]/td/font/a/text()')[0]
			return [ticker, longName]
		except Exception, e:
			print "CUSIP Unable to be found in TickerLookup, xmlScraper.py"
			print e
			print "cusip: " + cusip
			return 
		


