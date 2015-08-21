import keys
import MySQLdb
from EquityDataUpdater import *
import time


class HoldingAnalysis(object):
	
	def timerWrap(func):
		def timed(*args, **kw):
			ts = time.time()
			result = func(*args, **kw)
			te = time.time()
			print '%r (%r, %r) %2.2f sec' %(func.__name__, args, kw, te-ts)
			return result
		return timed	

	#ticker, name, shares held, marketValueThen, %portfolio, %previous portfolio, 
	#changes in shares, %change in portfolio size 

	#pulls holding information and tickers
	#**********do something if incorrect date
	@timerWrap
	def pullHoldings(self, cik, quarterDate):
		
		def consolidateAmmended():
			for filing in ammended:
				cur.execute("SELECT CUSIPList.Ticker, 13FHoldings.CUSIP, 13FHoldings.nameOfIssuer, 13FHoldings.titleOfClass, 13FHoldings.value, \
								13FHoldings.sshPrnamt, 13FHoldings.sshPrnamtType, 13FHoldings.putCall, 13FHoldings.investmentDiscretion, 13FHoldings.Sole, \
								13FHoldings.Shared, 13FHoldings.None \
								FROM CUSIPList INNER JOIN 13FHoldings \
								ON CUSIPList.CUSIP = 13FHoldings.CUSIP \
								WHERE 13FHoldings.accessionNunber = {}".format(filing[1]))
				#print [x for x in cur.fetchall()]	
				for holding in cur.fetchall():
					#holding ('QCOM', '747525103', 'QUALCOMM INC', 'COM', 327104L, 4400705L, 'SH', 'n/a', 'SOLE', 4400705L, 0L, 0L)
					cusipCompare = [hold for hold in holdingList if (holding[1] in hold and holding[7] in hold)]
					if not cusipCompare:
						holdingList.append(holding)


		holdingList = []
		db = MySQLdb.connect(host = keys.sqlHost, user = keys.sqlUsername, passwd = keys.sqlPassword, db="Quarterly13Fs") 
		with closing(db.cursor()) as cur:
			#*******Should i instead have a linking table?
			#http://stackoverflow.com/questions/5446778/sql-select-from-one-table-matching-criteria-in-another
			#cur.execute("SELECT * FROM 13FHoldings WHERE accessionNunber \
			#	IN (SELECT accessionNunber FROM 13FList WHERE cik = '%s' \
			#		AND quarterDate = '%s')" %(cik, quarterDate))
			
			query = "SELECT filingDate, accessionNunber, filingType FROM 13FList WHERE cik = '{}' AND quarterDate = '{}'".format(cik, quarterDate)
			cur.execute(query)
			entryList = [x for x in cur.fetchall()]	

			ammended = sorted([(amd[0],amd[1]) for amd in entryList if "13F-HR/A" in amd], key = lambda x: x[1], reverse=True)
			if ammended:
				consolidateAmmended()
			
			cur.execute("SELECT CUSIPList.Ticker, 13FHoldings.CUSIP, 13FHoldings.nameOfIssuer, 13FHoldings.titleOfClass, 13FHoldings.value, \
							13FHoldings.sshPrnamt, 13FHoldings.sshPrnamtType, 13FHoldings.putCall, 13FHoldings.investmentDiscretion, 13FHoldings.Sole, \
							13FHoldings.Shared, 13FHoldings.None \
							FROM CUSIPList INNER JOIN 13FHoldings \
							ON CUSIPList.CUSIP = 13FHoldings.CUSIP \
							WHERE 13FHoldings.accessionNunber IN \
							(SELECT accessionNunber FROM 13FList WHERE cik = '%s' AND quarterDate = '%s' AND filingType = '13F-HR')" %(cik, quarterDate))

			for holding in cur.fetchall():
				cusipCompare = [hold for hold in holdingList if (holding[1] in hold and holding[7] in hold)]
				if not cusipCompare:
					holdingList.append(holding)
		db.close()

		return holdingList

	#@timerWrap
	def calculateWeights(self, entryList, minFundWeight=0):
		marketCap = 0
		for entry in entryList:
			marketCap += entry[4]
		portfolio = []
		for entry in entryList:
			if entry[4]/float(marketCap) > minFundWeight:
				portfolio.append([entry[0], entry[4]/float(marketCap)])
		print portfolio
		return portfolio

	#minPortfolioWeight is the minimum weight a position can have in the total portfolio
	#minFundWeight is the minimum weight a position can be in the individual portoflios to be included
	#*********combine calls and stocks?
	@timerWrap
	def generatePortfolio(self, members, quarterDate, minPortfolioWeight = 0, minFundWeight=0):
		#********handle if quarter date isn't available yet
		#********handle if missing ticker information
		portfolio = {}
		for cik, weight in members.iteritems():
			fundPortfolio = self.calculateWeights(self.pullHoldings(cik, quarterDate), minFundWeight)
			for holding in fundPortfolio:
				portfolio[holding[0]] = "{0:.5f}".format(float(portfolio.get(holding[0], 0.0)) + holding[1]*weight)
		#from here on just cleans up if minPortfolioWeight is used
		if minPortfolioWeight:
			portfolioSize = 1.0
			toRemove = []
			updatedPortfolio = {}
			#************There could be a way to recursively do these loops? something to think about
			for ticker, weight in portfolio.iteritems():
				if float(weight) < minPortfolioWeight:
					toRemove.append(ticker)
					portfolioSize -= float(weight)
			for ticker in toRemove:
				portfolio.pop(ticker)
			for ticker, weight in portfolio.iteritems():
				updatedPortfolio[ticker] = "{0:.5f}".format(float(weight)/portfolioSize)
			self.printPortfolio(updatedPortfolio)
			return updatedPortfolio
		else:
			self.printPortfolio(portfolio)
			return portfolio

	#**********This is not done
	@timerWrap
	def changeInHoldings(self, cik, quarterDate1, quarterDate2):
		#ticker, currentShares, MarketValue, %Portfolio, %previousPortfolio, change in shares, %change
		entryList1 = self.pullHoldings(cik, quarterDate1)
		portfolio1 = self.calculateWeights(entryList1)
		entryList2 = self.pullHoldings(cik, quarterDate2)
		portfolio2 = self.calculateWeights(entryList2)
		#('ACT', 'G0083B108', 'ACTAVIS PLC', 'SHS', 205928L, 800000L, 'SH', 'n/a', 'SOLE', 800000L, 0L, 0L)
		#['ACT', 0.08212485827511795],

	#takes portfolio as dicitonary and prints it out nicely
	def printPortfolio(self, portfolio):
		orderedPortfolio = sorted(portfolio.items(), key=lambda x: x[1], reverse=True)
		for positionPair in orderedPortfolio:
			print positionPair[0], " ", "{0:.2%}".format(float(positionPair[1]))

	







