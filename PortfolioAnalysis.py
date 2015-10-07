from Portfolio import Portfolio
import numpy as np
import pandas as pd
import pandas.io.data as web
from pandas import DataFrame
from datetime import datetime



class PortfolioAnalysis(object):
    def __init__(self, portfolio, start_date, end_date):
        self.portfolio = portfolio.copy()
        self.start_date = start_date
        self.end_date = end_date

    def get_portfolio_performance(self):
        self.get_price_data()
        self.calculate_pct_chg()
        print self.portfolio
        return self.calculate_return()

    #***Could have DB that stores prices on specific days
    #***multiprocess
    def get_price_data(self):
        tickers = self.portfolio['ticker']
        for ticker in tickers:
            price_data = self.request_price_data(ticker)
            if price_data is not None and price_data.any():
                self.portfolio.loc[self.portfolio.ticker==ticker, 'startdate'] = price_data[0]
                self.portfolio.loc[self.portfolio.ticker==ticker, 'enddate'] = price_data[-1]

    def request_price_data(self,ticker):
        try:
            priceData = web.DataReader(ticker, 'yahoo', self.start_date,
                                       self.end_date)['Close']
            #***Handle Empty data better
            if priceData.empty: return None
            return priceData
        except IOError:
            print 'YAHOO Data Access for {} Failed'.format(ticker)
        try:
            priceData = web.DataReader(ticker, 'google', self.start_date,
                                    self.end_date)
            if priceData.empty: return None
            return priceData
        except IOError:
            print 'Google Data Access for {} Failed'.format(ticker)
        return
    #def get_price_data(self, datetype, date):
    #    date = datetime.strptime(date, '%Y-%m-%d')
    #    price_func = lambda x: web.DataReader(x, 'yahoo', date).iloc[0]['Close']
    #    self.portfolio[datetype] = self.portfolio['ticker'].map(price_func)

    def calculate_pct_chg(self):
        pct_chg_func = lambda x: (x['enddate']-x['startdate'])/x['startdate']
        self.portfolio['pctchg'] = self.portfolio.apply(pct_chg_func, axis=1)

    def calculate_return(self):
        return (self.portfolio['pctchg']*self.portfolio['weight']).sum()


if __name__ == '__main__':
    portfolio = Portfolio([('1336528', 1.0)], '2014-12-31')
    #portfolio = Portfolio([('1167483', 1.0)], '2014-12-31')
    pa = PortfolioAnalysis(portfolio.portfolio.copy(), '2015-01-01','2015-03-31')
    portfolio_return = pa.get_portfolio_performance()
    print portfolio_return

