import keys
import MySQLdb
from EquityDataUpdater import *
import time

#***********Should differentiate between holdings and calls


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
	#Both either Filing Date or quarter date, not both, not neither
	#@timerWrap
	def pullHoldings(self, cik, quarterDate = None, filingDate = None):

		fieldsSQLList = '''CUSIPList.Ticker, 13FHoldings.CUSIP, 13FHoldings.nameOfIssuer, 13FHoldings.titleOfClass, 
								13FHoldings.value, 13FHoldings.sshPrnamt, 13FHoldings.sshPrnamtType, 13FHoldings.putCall, 
								13FHoldings.investmentDiscretion, 13FHoldings.Sole, 13FHoldings.Shared, 13FHoldings.None'''
		def consolidateAmmended():
			for filing in ammended:
				cur.execute("SELECT {} FROM CUSIPList INNER JOIN 13FHoldings \
								ON CUSIPList.CUSIP = 13FHoldings.CUSIP \
								WHERE 13FHoldings.accessionNunber = {}".format(fieldsSQLList, filing[1]))
				#print [x for x in cur.fetchall()]	
				for holding in cur.fetchall():
					#holding ('QCOM', '747525103', 'QUALCOMM INC', 'COM', 327104L, 4400705L, 'SH', 'n/a', 'SOLE', 4400705L, 0L, 0L)
					cusipCompare = [hold for hold in holdingList if (holding[1] in hold and holding[7] in hold)]
					if not cusipCompare:
						holdingList.append(holding)

		if (quarterDate and filingDate) or (not filingDate and not quarterDate):
			print "ERROR: must choose EITHER quarter or filingDate"
			return
		elif filingDate:
			quarterDate = self.calculateQuarterDate(filingDate)
			print 'filingDate ' + filingDate
			print 'calculated quarterdate as ' + quarterDate 
		#****really scrubby, setting super high filing date so that it won't affect method
		else:
			filingDate = "3"+quarterDate[1:]
			print 'filingDate ' +filingDate


		holdingList = []
		db = MySQLdb.connect(host = keys.sqlHost, user = keys.sqlUsername, passwd = keys.sqlPassword, db="Quarterly13Fs") 
		with closing(db.cursor()) as cur:
			#*******Should i instead have a linking table?
			#http://stackoverflow.com/questions/5446778/sql-select-from-one-table-matching-criteria-in-another
			#cur.execute("SELECT * FROM 13FHoldings WHERE accessionNunber \
			#	IN (SELECT accessionNunber FROM 13FList WHERE cik = '%s' \
			#		AND quarterDate = '%s')" %(cik, quarterDate))
			
			entryList = None
			failCount = 0
			while not entryList and failCount <3:
				query = "SELECT filingDate, accessionNunber, filingType FROM 13FList WHERE cik = '{}' AND quarterDate = '{}'\
								AND filingDate <= '{}' ".format(cik, quarterDate, filingDate)
				cur.execute(query)
				entryList = [x for x in cur.fetchall()]	
				if entryList: break
				else: 
					failCount +=1
					quarterDate = self.calculateQuarterDate(quarterDate[0:8] + "25")
					print 'Updated QuarterDate to ' + str(quarterDate)


			ammended = sorted([(amd[0],amd[1]) for amd in entryList if "13F-HR/A" in amd], key = lambda x: x[1], reverse=True)
			if ammended:
				consolidateAmmended()
			
			cur.execute("SELECT {} FROM CUSIPList INNER JOIN 13FHoldings \
							ON CUSIPList.CUSIP = 13FHoldings.CUSIP \
							WHERE 13FHoldings.accessionNunber IN \
							(SELECT accessionNunber FROM 13FList WHERE cik = '{}' AND quarterDate = '{}' \
							AND filingType = '13F-HR' AND filingDate <= '{}')".format(fieldsSQLList, cik, quarterDate, filingDate))
			for holding in cur.fetchall():
				cusipCompare = [hold for hold in holdingList if (holding[1] in hold and holding[7] in hold)]
				if not cusipCompare:
					holdingList.append(holding)
		db.close()

		#print holdingList
		return holdingList


	def calculateQuarterDate(self, filingTime):
		qy = int(filingTime[0:4])
		qm = int(filingTime[5:7])
		qd = int(filingTime[8:])

		quarterYear = None
		quarterMonth = None
		quarterDay = None

		if qm < 3 or (qm ==3 and qd <31):
			quarterYear = qy - 1
			quarterMonth = 12
		elif qm < 6 or (qm==6 and qd < 30):
			quarterMonth = 3
			quarterYear = qy
		elif qm < 9 or (qm==9 and qd<30):
			quarterMonth = 6
			quarterYear = qy
		elif qm <12 or (qm == 12 and qd <31):
			quarterMonth = 9
			quarterYear = qy
		else: 
			quarterMonth = 12
			quarterYear = qy

		if quarterMonth in [3, 12]:
			quarterDay = 31
		else:
			quarterDay = 30
		return str(datetime.date(quarterYear, quarterMonth, quarterDay))


	#@timerWrap
	def calculateWeights(self, entryList, minFundWeight=0):
		marketCap = 0
		for entry in entryList:
			marketCap += entry[4]
		portfolio = []
		for entry in entryList:
			if entry[4]/float(marketCap) > minFundWeight:
				portfolio.append([entry[0], entry[4]/float(marketCap)])
		#print portfolio
		return portfolio

	#minPortfolioWeight is the minimum weight a position can have in the total portfolio
	#minFundWeight is the minimum weight a position can be in the individual portoflios to be included
	#*********combine calls and stocks?
	@timerWrap
	def generatePortfolio(self, members, quarterDate = None, filingDate = None, minPortfolioWeight = 0, minFundWeight=0):
		#********handle if quarter date isn't available yet
		#********handle if missing ticker information
		if (quarterDate and filingDate) or (not filingDate and not quarterDate):
			print "ERROR: must choose EITHER quarter or filingDate"
			return

		portfolio = {}
		for cik, weight in members.iteritems():
			fundPortfolio = self.calculateWeights(self.pullHoldings(cik, quarterDate, filingDate), minFundWeight)
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
			#self.printPortfolio(updatedPortfolio)
			return updatedPortfolio
		else:
			#self.printPortfolio(portfolio)
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


#****need to go by filingDate
class PortfolioPerformance(HoldingAnalysis):
	
	def portfolioPerformance(self, members, startDate, endDate, minPortfolioWeight = 0, minFundWeight=0):
		#list of tuples. tuples are date, portfolioDict
		portfolioList = self.generateListOfPortfolios(members, startDate, endDate, minPortfolioWeight, minFundWeight)
		
		



	def generateListOfPortfolios(self, members, startDate, endDate, minPortfolioWeight, minFundWeight):
		ciks = []
		for cik, weight in members.iteritems():
			ciks.append(cik)
		portfolioList = []
		#first portfolio
		portfolioList.append((datetime.datetime.strptime(startDate, "%Y-%m-%d").date(), 
			self.generatePortfolio(members, None, startDate, minPortfolioWeight, minFundWeight)))

		changeDatesList = self.portfolioChangeDates(ciks,startDate,endDate)
		for dateChange in changeDatesList:
			portfolioList.append((dateChange, self.generatePortfolio(members, None, dateChange.strftime('%Y-%m-%d'))))
		portfolioList.sort(key= lambda x: x[0])
		return portfolioList

#****may have to add 1 to change list date
#returns list of dates of new releases
	def portfolioChangeDates(self, ciks, startDate, endDate):
		changeList = []
		db = MySQLdb.connect(host = keys.sqlHost, user = keys.sqlUsername, passwd = keys.sqlPassword, db="Quarterly13Fs") 
		with closing(db.cursor()) as cur:
			for cik in ciks:
				cur.execute("SELECT filingDate FROM 13FList WHERE cik = {} AND filingDate >= '{}'\
					AND filingDate <= '{}'".format(cik, startDate, endDate))
				for pChange in cur.fetchall():
					changeList.append(pChange[0])
					
		db.close()
		return changeList


	def portfolioPerformance(self, startDate, endDate, portfolio):
		

























