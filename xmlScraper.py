#13F scraper

#http://www.sec.gov/cgi-bin/browse-edgar?CIK=0001167483&action=getcompany&type=13f
#cik: is the firm identification number
#action: needs to equal getcompany
#type: 13f narrows it down
#http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&
	#CIK=0001167483&type=13f&start=0&count=40&output=atom
#this is the RSS feed
#provides the filing-date and filing-href

from lxml import etree
import lxml
import requests

import xml.etree.cElementTree as ET

#Notes
#Don't need zeros in front of CIK and should take those out at the initial upload level

class UpdateChecker(object):

	#checks database for most recent 13F and returns the last date
	#checks to see whether or not a 13F should even be available
	def mostRecentForm13F(self, cik):
		pass
		#return lastDate

	#***check the dates i have and which i should upload
	#check whether there are 40 lists, if so i need to run again
	def get13FList(self, cik, lastDate = None):
		rssListString = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%s&type=13f&start=0&count=40&output=atom" % (cik)
		page = requests.get(rssListString)
		tree = etree.fromstring(page.content)
		namespace = "{%s}" % (tree.nsmap[None])
		entryElements = tree.findall('{0}entry'.format(namespace))
		entries = self.cleanEntryElements(entryElements, namespace)

		#entries is a list of lists.  list has accessionNunber and date	
		return entries

	def cleanEntryElements(self, entryElements, namespace):
		entries = []
		for entry in entryElements:
			#yes it is nunber
			#get and clean accession from "-"
			accessionNunber = entry.find('{0}content/{0}accession-nunber'.format(namespace)).text.replace("-","")
			filingDate = entry.find('{0}content/{0}filing-date'.format(namespace)).text
			entries.append([accessionNunber,filingDate])
		return entries


class Form13FUpdater(object):
	#initializes class with the CIK and a 2d list called entires
	#the CIK is the identification number of the Firm
	#entries is a list containing lists of as accessionNunbers and filing dates 
	def __init__(self, cik, entries):
		self.cik = cik
		self.entries = entries

	#entryParser goes through the entry list, and calls scrapeForm13F which returns infoTables
	#it then passes infoTables to uploadForm13F
	def entryParser(self):
		for entry in self.entries:
			accessionNunber = entry[0]
			filingDate = entry[1]
			infoTables = self.scrapeForm13F(accessionNunber)
			print infoTables
			self.uploadForm13F(accessionNunber, infoTables)

	#scrapeForm13F takes teh accessionNunber as an argurment then downloads an xml with the 
	#data. And puts all of the "infoTables" from the file into a list called infoTableElements
	#it then calls cleanInfoTableElements which returns a cleaned infoTables
	#this function returns infoTables
	def scrapeForm13F(self, accessionNunber):
		#http://www.sec.gov/Archives/edgar/data/1167483/000091957414004747/infotable.xml
		#data/CIKwoZeros/Accession-nunber/infotable.xml
		xmlURLString = "http://www.sec.gov/Archives/edgar/data/{0}/{1}/infotable.xml".format(self.cik, accessionNunber)
		page = requests.get(xmlURLString)
		tree = etree.fromstring(page.content)
		namespace = "{%s}" % (tree.nsmap[None])
		infoTableElements = tree.findall('{0}infoTable'.format(namespace))
		infoTables = self.cleanInfoTableElements(infoTableElements, namespace)
		return infoTables

	#clean InfoTableElements takes infoTableElements and the namespace of the xml as 
	#parameters
	def cleanInfoTableElements(self, infoTableElements, namespace):
		def createInfoDict(keys):
			infoDict = {}
			for key, path in keys.iteritems():
				infoDict[key] = infoTable.find(path.format(namespace)).text
			return infoDict

		infoTables = []
		for infoTable in infoTableElements:
			keys = {
				'nameOfIssuer': '{0}nameOfIssuer',
				'titleOfClass': '{0}titleOfClass',
				'cusip': '{0}cusip',
				'value': '{0}value',
				'sshPrnamt': '{0}shrsOrPrnAmt/{0}sshPrnamt',
				'sshPrnamtType': '{0}shrsOrPrnAmt/{0}sshPrnamtType',
				'investmentDiscretion': '{0}investmentDiscretion',
				'Sole': '{0}votingAuthority/{0}Sole',
				'Shared': '{0}votingAuthority/{0}Shared',
				'None': '{0}votingAuthority/{0}None'
			}
			#appends infoDict to infoTables
			infoTables.append(createInfoDict(keys))
			
		return infoTables
			




	def uploadForm13F(self, accessionNunber, infoTables):
		pass

