import keys
import MySQLdb
from EquityDataUpdater import *


class HoldingAnalysis(object):
	#ticker, name, shares held, marketValueThen, %portfolio, %previous portfolio, 
	#changes in shares, %change in portfolio size 

	def pullHoldings(self, cik, quarterDate):
		entryList = []
		db = MySQLdb.connect(host = keys.sqlHost, user = keys.sqlUsername, passwd = keys.sqlPassword, db="Quarterly13Fs") 
		with closing(db.cursor()) as cur:
			#*******Should i instead have a linking table?
			#http://stackoverflow.com/questions/5446778/sql-select-from-one-table-matching-criteria-in-another
			cur.execute("SELECT * FROM 13FHoldings WHERE accessionNunber \
				IN (SELECT accessionNunber FROM 13FList WHERE cik = '%s' \
					AND quarterDate = '%s')" %(cik, quarterDate))
			entryList = [x for x in cur.fetchall()]	
		db.close()
		return entryList
		#(5300L, '000091957414006596', '21VIANET GROUP INC', 'SPONSORED ADR', '90138A103', 36000L, 2000000L, 'SH', 'n/a', 'SOLE', 2000000L, 0L, 0L)

	#*********This should just get tickers and not organize
	def getTickersAndOrganize(self, entryList):
		portfolio = []
		portfolioMarketCap = 0
	 	db = MySQLdb.connect(host = keys.sqlHost, user = keys.sqlUsername, passwd = keys.sqlPassword, db="Quarterly13Fs") 
		with closing(db.cursor()) as cur:
			for entry in entryList:
				cusip = entry[4]
				cur.execute("SELECT Ticker from CUSIPList WHERE CUSIP = '%s'" %(cusip))
				#********may have to catch here if i don't have the ticker in my database
				ticker = cur.fetchone()[0]
				portfolioMarketCap += entry[5]
				portfolio.append([ticker, entry[2], entry[6], entry[5]])
		db.close()

		totalPos = 0
		for lineItem in portfolio:
			positionSize = lineItem[3]/float(portfolioMarketCap)*100
			totalPos += positionSize
			lineItem.append(positionSize)

		print portfolio
		print portfolioMarketCap


class PortfolioGenerator(object):
	#intializes with a dictionary of member ciks and portfolio weights
	def __init__(self, members, portfolioDate=None):
		
		#***********Do I really want the class to be initalized with the members and date?
		#***Probably not, should just be taken in a method i would think...maybe...don'tknow
		self.members = members
		self.portfolioDate = portfolioDate



	#****Don't think this should actually be in this class
	def pullHoldings(self):
		#db = MySQLdb.connect(host = keys.sqlHost, user = keys.sqlUsername, passwd = keys.sqlPassword, db="Quarterly13Fs") 
		#with closing(db.cursor()) as cur:
		#	for member in members:
		#
		#	cur.execute("SELECT MAX(filingDate) FROM 13FList WHERE CIK=%s" %(cik))
		#	lastDate = cur.fetchone()[0]

		#db.close()
		pass