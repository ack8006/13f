from xmlScraper import UpdateChecker, Form13FUpdater
import MySQLdb
from contextlib import closing
from datetime import datetime, date
#from datetime import date

db = MySQLdb.connect(host="127.0.0.1",user = "user1", passwd = "password", db="Quarterly13Fs")

cikList = []

with closing(db.cursor()) as cur:
	cur.execute("SELECT CIK FROM CIKList")
	cikList = [x[0] for x in cur.fetchall()]	

db.close()

upCheck = UpdateChecker()
#DAYS_TO_CHECK_FOR_UPDATES = 82
DAYS_TO_CHECK_FOR_UPDATES =95

for cik in cikList:
	lastDate = upCheck.mostRecentForm13F(cik)
	print lastDate
	if not lastDate or (lastDate and abs(date.today()-lastDate).days > DAYS_TO_CHECK_FOR_UPDATES):
		entries = upCheck.get13FList(cik, lastDate)
		formUpdate = Form13FUpdater(cik, entries)
		formUpdate.entryParser()
