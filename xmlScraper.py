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

from lxml import etree

import MySQLdb
import requests
import lxml
from contextlib import closing
import datetime



import xml.etree.cElementTree as ET

#**************Files were submitted as text files prior to 3Q13...shit

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
		db = MySQLdb.connect(host="127.0.0.1",user = "user1", passwd = "password", db="Quarterly13Fs")
		lastDate = None
		with closing(db.cursor()) as cur:
			cur.execute("SELECT MAX(filingDate) FROM 13FList WHERE CIK=%s" %(cik))
			lastDate = cur.fetchone()[0]
		db.close()
		return lastDate

	#********check the dates i have and which i should upload
	#********check whether there are 40 lists, if so i need to run again
	def get13FList(self, cik, lastDate = None):
		rssListString = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%s&type=13f&start=0&count=40&output=atom" % (cik)
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
			accessionNunber = entry.find('{0}content/{0}accession-nunber'.format(namespace)).text.replace("-","")
			filingDate = entry.find('{0}content/{0}filing-date'.format(namespace)).text
			#converst filingDate to a datetime format so it can be compared to the last date in datetime format
			filingTime = datetime.datetime.strptime(filingDate, "%Y-%m-%d").strftime('%Y-%m-%d %H:%M:%S')
			if (filingTime <= lastDate):
				print filingDate
				return entries
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
		for entry in self.entries:
			accessionNunber = entry[0]
			filingDate = entry[1]
			infoTables = self.scrapeForm13F(accessionNunber)
			#the only reason it wouldn't be info tables is if the http request is not 200
			if infoTables:
				#uploads the holdings into the database, the form info to 13FList
				self.upload13FHoldings(accessionNunber, filingDate, infoTables)

				#***********Should take this opportunity to update CUSIP Database 
				#Maybe in the process can implement fuzzywuzzy library when looking up cusip and tickers


	#scrapeForm13F takes the accessionNunber as an argurment then downloads an xml with the 
	#data. And puts all of the "infoTables" from the file into a list called infoTableElements
	#it then calls cleanInfoTableElements which returns a cleaned infoTables
	#this function returns infoTables
	def scrapeForm13F(self, accessionNunber):
		#http://www.sec.gov/Archives/edgar/data/1167483/000091957414004747/infotable.xml
		#data/CIKwoZeros/Accession-nunber/infotable.xml
		xmlURLString = "http://www.sec.gov/Archives/edgar/data/{0}/{1}/infotable.xml".format(self.cik, accessionNunber)
		page = requests.get(xmlURLString)
		#checks if page returns
		if page.status_code == 200:
			tree = etree.fromstring(page.content)
			namespace = "{%s}" % (tree.nsmap[None])
			infoTableElements = tree.findall('{0}infoTable'.format(namespace))
			infoTables = self.cleanInfoTableElements(infoTableElements, namespace)
			print infoTables
			return infoTables
		else:
			return 

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
		db = MySQLdb.connect(host="127.0.0.1",user = "user1", passwd = "password", db="Quarterly13Fs")

		#load the data into 13FHoldings and if successful then add to the 13FList database

		with closing(db.cursor()) as cur:
			#belt and suspenders check here to see if the accessiionNunber is already in
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

				#makes date object
				filingTime = datetime.datetime.strptime(filingDate, "%Y-%m-%d").strftime('%Y-%m-%d %H:%M:%S')

				cur.execute("INSERT INTO 13FList (CIK, filingDate, accessionNunber) \
					VALUES('%s', '%s', '%s')"
					%(self.cik, filingTime, accessionNunber))

				db.commit()

			else:
				#****Should log some error here if gets to this point and it has somethings in there already
				pass


		db.close()	







