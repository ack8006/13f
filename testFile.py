
from xmlScraper import UpdateChecker, Form13FUpdater
import datetime
from HoldingAnalysis import *
from EquityDataUpdater import *



def main():

	#upCheck = UpdateChecker()
	#cik = "1167483" #tiger
	cik = "1336528" #persh
	#cik = "1582090" #sachem
	#cik = "1569175" #tigereye
	
	#lastDate = mostRecentFormTest(upCheck, cik)
	#entries = get13FListTest(upCheck, cik, lastDate)

	#date1 = filingTime = datetime.datetime.strptime('2010-02-16', "%Y-%m-%d").strftime('%Y-%m-%d %H:%M:%S')
	#entries = get13FListTest(upCheck, cik, date1)
	
	#date2 = filingTime = datetime.datetime.strptime('2014-08-14', "%Y-%m-%d").strftime('%Y-%m-%d %H:%M:%S')
	#entries = get13FListTest(upCheck, cik, date2)


	#entries = [['000091957414004747', '2014-08-14']]
	
	#formUpdate = Form13FUpdater(cik, entries)
	#entryParserTest(formUpdate)
	
	#connectionCheckTest(formUpdate)

	#cusip = "G5258J109"
	#cusipList = ['N51488117', '62855J104', '65440R101', '741503403','74906P104','761152107','G87210103']
	#for cusip in cusipList:
	#	tickerLookupTest(formUpdate, cusip)

#EquityDataUpdater
	#equityDataUpdater = EquityDataUpdater()
	#priceData = getPriceDataTest(equityDataUpdater, "AAPL", startDate = "2015-1-31")
	#updateLastPriceDatabaseTest(equityDataUpdater, ["XOM"])

#HoldingAnalysis
	holdingAnalysis = HoldingAnalysis()
	#holdings = pullHoldingsTest(holdingAnalysis,"1336528", "2014-09-30")
	#portfolio = calculateWeightsTest(holdingAnalysis, holdings)
	#portfolio = generatePortfolio(holdingAnalysis, {'1167483': 0.4, '1336528':0.3, '1582090':0.3}, "2014-12-31")
	portfolio = generatePortfolio(holdingAnalysis, {'1167483': 0.34, '1336528':0.33, '1582090':0.33}, "2014-12-31", 0.015, 0.0)
	portfolioChange = changeInHoldings(holdingAnalysis, '1167483',"2014-12-31","2014-09-30")

def mostRecentFormTest(upCheck, cik):
	lastDate = upCheck.mostRecentForm13F(cik)
	print lastDate
	return lastDate

def get13FListTest(upCheck, cik, lastDate):
	entries = upCheck.get13FList(cik, lastDate)
	print entries
	return entries

def entryParserTest(formUpdate):
	formUpdate.entryParser()

def connectionCheckTest(formUpdate):
	formUpdate.upload13FHoldings("test","test")

def tickerLookupTest(formUpdate, cusip):
	formUpdate.tickerLookup(cusip)

#EquityDataUpdater
def getPriceDataTest(equityDataUpdater, ticker, startDate=None, endDate=None, priceType=4):
	return equityDataUpdater.getPriceData(ticker,startDate,endDate,priceType)

def updateLastPriceDatabaseTest(equityDataUpdater, ticker):
	return equityDataUpdater.updateLastPriceDatabase(ticker)

#Holding Analysis
def pullHoldingsTest(holdingAnalysis, cik, quarterDate):
	return holdingAnalysis.pullHoldings(cik, quarterDate)

def calculateWeightsTest(holdingAnalysis, holdings, minFundWeight = 0):
	return holdingAnalysis.calculateWeights(holdings, minFundWeight)

def generatePortfolio(holdingAnalysis, members, quarterDate, minPortfolioWeight = 0, minFundWeight=0):
	return holdingAnalysis.generatePortfolio(members, quarterDate, minPortfolioWeight, minFundWeight)	

def changeInHoldings(holdingAnalysis, cik, quarterDate1, quarterDate2):
	return holdingAnalysis.changeInHoldings(cik, quarterDate1, quarterDate2)	

if __name__ == "__main__":
    main()


