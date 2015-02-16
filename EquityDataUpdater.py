import keys
import MySQLdb
import requests
import datetime
from contextlib import closing


class EquityDataUpdater(object):
	#https://www.quandl.com/api/v1/datasets/WIKI/AAPL.csv?sort_order=dsc&exclude_headers=true&rows=3&trim_start=2012-11-01&trim_end=2013-11-30&column=4&collapse=quarterly&transformation=rdiff

	#Column
	#1 open
	#2 high
	#3 low
	#4 close 
	#5 volume
	#6 dividends and splits, and split/dividend adjusted open, high, low close and volume for Apple Inc.
	
	#returns dictionary of priceData with yyyy-mm-dd at key
	def getPriceData(self, ticker, startDate = None, endDate = None, priceType = 4, rows = None):
		baseURL = self.generateURL(ticker, startDate, endDate, priceType, rows)

		page = requests.get(baseURL)

		priceDataList = page.json()['data']
		priceData = {dataPair[0]:dataPair[1] for dataPair in priceDataList}

		return priceData
	
	#takes list of tickers, and updates the database
	def updateLastPriceDatabase(self, tickers):
		priceDataList = []
		for ticker in tickers:
			priceData = self.getPriceData(ticker, None, None, 4, 1)
			dataPair = priceData.iteritems().next()
			priceDataList.append([ticker, dataPair])

		db = MySQLdb.connect(host = keys.sqlHost, user = keys.sqlUsername, passwd = keys.sqlPassword, db="Quarterly13Fs") 
		with closing(db.cursor()) as cur:
			for priceData in priceDataList:
				ticker = priceData[0]
				lastPriceDate = datetime.datetime.strptime(priceData[1][0], '%Y-%m-%d')
				lastPrice = priceData[1][1]

				cur.execute("UPDATE CUSIPList SET LastPrice = '%s', LastPriceDate = '%s' \
					WHERE Ticker = '%s'" %(lastPrice, lastPriceDate, ticker))

		db.commit()
		db.close()

	def generateURL(self, ticker, startDate=None, endDate=None, priceData = 4, rows = None, collapse = None, transformation = None):
		baseURL = "https://www.quandl.com/api/v1/datasets/WIKI/%s.json?auth_token=%s" %(ticker, keys.quandlAPI)
		if startDate:
			baseURL = baseURL + "&trim_start=%s" %(startDate) 
		if endDate:
			baseURL = baseURL + "&trim_end=%s" %(endDate)
		baseURL = baseURL + "&column=%s" %priceData
		if rows:
			baseURL = baseURL + "&rows=%s" %(rows)
		if collapse:
			baseURL = baseURL + "&collapse=%s" %(collapse)
		if transformation:
			baseURL = baseURL + "&transformation=%s" %(transformation)

		return baseURL