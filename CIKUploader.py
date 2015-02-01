import MySQLdb
import csv
from contextlib import closing

f = open('ciks.csv')
csv_f = csv.reader(f)

counter = 1
db = MySQLdb.connect(host="127.0.0.1",user = "user1", passwd = "password", db="Quarterly13Fs")

with closing(db.cursor()) as cur:
	for row in csv_f:
		firmName = None
		CIK = None
		if counter >1:
			firmName = row[0]
			CIK = row[1]
			cur.execute("SELECT COUNT(*) as count FROM CIKList WHERE CIK = %s" %(CIK))
			existingEntries = cur.fetchone()[0]
			if existingEntries <1:
				cur.execute("INSERT INTO CIKList (CIK, firmName) VALUES ('%s', '%s')" 
					% (CIK, firmName))
		counter += 1
	db.commit()
db.close()
		
