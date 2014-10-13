
from xmlScraper import xmlScraper



def main():

	xml = xmlScraper()
	cik = "1167483"
	get13FListTest(xml, cik)

	entries = [['000091957414004747', '2014-08-14']]
	setScrapeAndUploadTest(xml, cik, entries)


def get13FListTest(xml, cik):
	entries = xml.get13FList(cik)
	print entries

def setScrapeAndUploadTest(xml, cik, entries):
	xml.setScrapeAndUpload(cik, entries)



if __name__ == "__main__":
    main()