import keys
import MySQLdb


class PortfolioGenerator(object):
	#intializes with a dictionary of member ciks and portfolio weights
	def __init__(self, members, portfolioDate=None):
		self.members = members
		self.portfolioDate = portfolioDate

	def pullHoldings(self):
		db = MySQLdb.connect(host = keys.sqlHost, user = keys.sqlUsername, passwd = keys.sqlPassword, db="Quarterly13Fs") 
		with closing(db.cursor()) as cur:
			for member in members:

			cur.execute("SELECT MAX(filingDate) FROM 13FList WHERE CIK=%s" %(cik))
			lastDate = cur.fetchone()[0]

		db.close()