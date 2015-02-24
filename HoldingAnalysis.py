import keys
import MySQLdb
from EquityDataUpdater import *


class HoldingAnalysis(object):
	#ticker, name, shares held, marketValueThen, %portfolio, %previous portfolio, 
	#changes in shares, %change in portfolio size 

	#pulls holding information and tickers
	def pullHoldings(self, cik, quarterDate):
		entryList = []
		db = MySQLdb.connect(host = keys.sqlHost, user = keys.sqlUsername, passwd = keys.sqlPassword, db="Quarterly13Fs") 
		with closing(db.cursor()) as cur:
			#*******Should i instead have a linking table?
			#http://stackoverflow.com/questions/5446778/sql-select-from-one-table-matching-criteria-in-another
			#cur.execute("SELECT * FROM 13FHoldings WHERE accessionNunber \
			#	IN (SELECT accessionNunber FROM 13FList WHERE cik = '%s' \
			#		AND quarterDate = '%s')" %(cik, quarterDate))
			cur.execute("SELECT CUSIPList.Ticker, 13FHoldings.CUSIP, 13FHoldings.nameOfIssuer, 13FHoldings.titleOfClass, 13FHoldings.value, \
							13FHoldings.sshPrnamt, 13FHoldings.sshPrnamtType, 13FHoldings.putCall, 13FHoldings.investmentDiscretion, 13FHoldings.Sole, \
							13FHoldings.Shared, 13FHoldings.None \
							FROM CUSIPList INNER JOIN 13FHoldings \
							ON CUSIPList.CUSIP = 13FHoldings.CUSIP \
							WHERE 13FHoldings.accessionNunber IN \
							(SELECT accessionNunber FROM 13FList WHERE cik = '%s' AND quarterDate = '%s')" %(cik, quarterDate))
			entryList = [x for x in cur.fetchall()]	
		db.close()
		#ticker, cusip, name, titleOfClass, value (1000s), shares, type, put call, investment discretion, sole, shared, none
		# ('PAH', '72766Q105', 'PLATFORM SPECIALTY PRODS COR', 'COM', 834000L, 33333330L, 'SH', 'n/a', 'SOLE', 33333330L, 0L, 0L)
		return entryList

	def calculateWeights(self, entryList):
		marketCap = 0
		for entry in entryList:
			marketCap += entry[4]
		portfolio = []
		for entry in entryList:
			#cusip, percent
			#************should it be a dict?
			#portfolio.append([entry[0], '{percent:.2%}'.format(percent=entry[4]/float(marketCap))])
			portfolio.append([entry[0], entry[4]/float(marketCap)])
		return portfolio

	def generatePortfolio(self, members, quarterDate):
		#********handle if quarter date isn't available yet
		#members = {cik:weight, cik:weight}
		portfolio = {}
		for cik, weight in members.iteritems():
			fundPortfolio = self.calculateWeights(self.pullHoldings(cik, quarterDate))
			print fundPortfolio
			for holding in fundPortfolio:
				portfolio[holding[0]] = "{0:.5f}".format(float(portfolio.get(holding[0], 0.0)) + holding[1]*weight)
		print portfolio








