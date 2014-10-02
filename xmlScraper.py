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

class xmlScraper():
	def initializeScrape(self, cik):
		self.get13FList(cik)

	def get13FList(self, cik):
		#first zeros unneeded

		rssListString = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%s&type=13f&start=0&count=40&output=atom" % (cik)
		page = requests.get(rssListString)
		tree = etree.fromstring(page.content)

		#*****STUCK HERE
		authors = tree.xpath('*')

	def scrape13F(self, accessionNumber):
		#http://www.sec.gov/Archives/edgar/data/1167483/000091957414004747/infotable.xml
		#data/CIKwoZeros/Accession-number/infotable.xml

		pass
		

#will delete when functional
def main():
	xml = xmlScraper()
	xml.initializeScrape("0001167483")


if __name__ == "__main__":
    main()