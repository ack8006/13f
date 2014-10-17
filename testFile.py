
from xmlScraper import UpdateChecker, Form13FUpdater



def main():

	upCheck = UpdateChecker()
	cik = "1167483"
	#entries = get13FListTest(upCheck, cik)

	entries = [['000091957414004747', '2014-08-14']]
	formUpdate = Form13FUpdater(cik, entries)
	entryParserTest(formUpdate)


def get13FListTest(upCheck, cik):
	entries = upCheck.get13FList(cik)
	print entries
	return entries

def entryParserTest(formUpdate):
	formUpdate.entryParser()



if __name__ == "__main__":
    main()