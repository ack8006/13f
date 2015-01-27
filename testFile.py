
from xmlScraper import UpdateChecker, Form13FUpdater



def main():

	upCheck = UpdateChecker()
	cik = "1167483"
	#cik = "1336528"
	#entries = get13FListTest(upCheck, cik)
	#entries = get13FListTest(upCheck, cik, '2010-02-16')
	entries = get13FListTest(upCheck, cik, '2014-08-14')


	#entries = [['000091957414004747', '2014-08-14']]
	
	formUpdate = Form13FUpdater(cik, entries)
	entryParserTest(formUpdate)
	#connectionCheckTest(formUpdate)


def get13FListTest(upCheck, cik, lastDate):
	entries = upCheck.get13FList(cik, lastDate)
	print entries
	return entries

def entryParserTest(formUpdate):
	formUpdate.entryParser()

def connectionCheckTest(formUpdate):
	formUpdate.uploadForm13F("test","test")

if __name__ == "__main__":
    main()