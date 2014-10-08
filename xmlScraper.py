#13F scraper

#http://www.sec.gov/cgi-bin/browse-edgar?CIK=0001167483&action=getcompany&type=13f
#cik: is the firm identification number
#action: needs to equal getcompany
#type: 13f narrows it down
#http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001167483&type=13f&start=0&count=40&output=atom
#this is the RSS feed
#provides the filing-date and filing-href

from lxml import etree
import lxml
import requests

import xml.etree.cElementTree as ET

#Notes

#Don't need zeros in front of CIK and should take those out at the initial upload level

class xmlScraper():
	def initializeScrape(self, cik):
		entries = self.get13FList(cik)
		self.setScrapeAndUpload(cik, entries)

	#***check the dates i have and which i should upload
	#check whether there are 40 lists, if so i need to run again
	def get13FList(self, cik):
		rssListString = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%s&type=13f&start=0&count=40&output=atom" % (cik)
		page = requests.get(rssListString)
		tree = etree.fromstring(page.content)

		namespace = "{%s}" % (tree.nsmap[None])

		entryElements = tree.findall('{0}entry'.format(namespace))
		
		entries = []
		for entry in entryElements:
			#yes it is nunber
			#get and clean accession from "-"
			accessionNunber = entry.find('{0}content/{0}accession-nunber'.format(namespace)).text.replace("-","")
			filingDate = entry.find('{0}content/{0}filing-date'.format(namespace)).text
			entries.append((accessionNunber,filingDate))

		#entries is a list of tuples.  tuple has accessionNunber and date	
		return entries

	def setScrapeAndUpload(self, cik, entries):
		for entry in entries:
			accessionNunber = entry[0]
			filingDate = entry[1]
			infoTables = self.scrape13F(accessionNunber)
			self.upload13F(cik, accessionNunber, infoTables)

	def scrape13F(self, accessionNunber):
		#http://www.sec.gov/Archives/edgar/data/1167483/000091957414004747/infotable.xml
		#data/CIKwoZeros/Accession-nunber/infotable.xml
		
		pass

	def upload13F(self, cik, accessionNunber, infoTables):
		pass

#will delete when functional
def main():
	xml = xmlScraper()
	xml.initializeScrape("0001167483")
	#xml.scrape13F()


if __name__ == "__main__":
    main()