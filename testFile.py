
import datetime
from UpdateChecker import UpdateChecker
from Form13FUpdater import Form13FUpdater
#from xmlScraper import UpdateChecker, Form13FUpdater
#from HoldingAnalysis import *
#from EquityDataUpdater import *



def main():

    #cik = "1167483" #tiger
    #cik = "1336528" #persh
	#cik = "1582090" #sachem
	#cik = "1569175" #tigereye
    #cik = "1159159" #Jana for testing ammended shit
    cik = "1389507" #disco

    upCheck = UpdateChecker(cik)
    entries = upCheck.get_13F_forms_to_update()
    print entries

    #entries = get13FListTest(upCheck, cik, lastDate)

	#date1 = filingTime = datetime.datetime.strptime('2010-02-16', "%Y-%m-%d").strftime('%Y-%m-%d %H:%M:%S')
	#entries = get13FListTest(upCheck, cik, date1)

	#date2 = filingTime = datetime.datetime.strptime('2014-08-14', "%Y-%m-%d").strftime('%Y-%m-%d %H:%M:%S')
	#entries = get13FListTest(upCheck, cik, date2)

	#tiger
	#entries = [['000091957415006282', '2015-08-14']]

    #entries = [{'filing_date': datetime.date(2015, 8, 14),
    #            'accession_nunber': '0000919574-15-006282',
    #            'filing_type': u'13F-HR',
    #            'updated_time': datetime.datetime(2015, 8, 14, 13, 52, 14)}]
    formUpdate = Form13FUpdater(cik, entries)
    formUpdate.update_entries()

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
	#holdingAnalysis = HoldingAnalysis()
	#holdings = pullHoldingsTest(holdingAnalysis,"1159159", "2014-09-30")
	#holdings = pullHoldingsTest(holdingAnalysis,"1159159", None, "2015-06-10")
	#portfolio = calculateWeightsTest(holdingAnalysis, holdings)
	#portfolio = generatePortfolio(holdingAnalysis, {'1167483': 0.4, '1336528':0.3, '1582090':0.3}, "2015-06-30")
	#portfolio = generatePortfolio(holdingAnalysis, {'1167483': 0.34, '1336528':0.33, '1582090':0.33}, "2014-12-31", 0.015, 0.0)
	#portfolio = generatePortfolio(holdingAnalysis, {1159159: 1.0}, "2015-03-31")
	#portfolioChange = changeInHoldings(holdingAnalysis, '1167483',"2015-03-31","2015-06-30")

	#pp = PortfolioPerformance()
	#pp.portfolioPerformance({'1159159': 1.0}, "2015-01-05", "2015-05-20", 0.025)


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
def pullHoldingsTest(holdingAnalysis, cik, quarterDate = None, filingDate = None):
	return holdingAnalysis.pullHoldings(cik, quarterDate, filingDate)

def calculateWeightsTest(holdingAnalysis, holdings, minFundWeight = 0):
	return holdingAnalysis.calculateWeights(holdings, minFundWeight)

def generatePortfolio(holdingAnalysis, members, quarterDate, minPortfolioWeight = 0, minFundWeight=0):
	return holdingAnalysis.generatePortfolio(members, quarterDate, minPortfolioWeight, minFundWeight)

def changeInHoldings(holdingAnalysis, cik, quarterDate1, quarterDate2):
	return holdingAnalysis.changeInHoldings(cik, quarterDate1, quarterDate2)

if __name__ == "__main__":
    main()


