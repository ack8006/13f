
from xmlScraper import xmlScraper



def main():

	xml = xmlScraper()
	cik = "0001167483"
	get13FListTest(xml, cik)


def get13FListTest(xml, cik):
	entries = xml.get13FList(cik)
	print entries

def setScrapeAndUploadTest(xml, cik, entries):
	

if __name__ == "__main__":
    main()