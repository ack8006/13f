from Portfolio import Portfolio
import numpy as np
import pandas as pd
import pandas.io.data as web
from pandas import DataFrame
from datetime import datetime
from dbconnection import start_db_connection
from contextlib import closing

DB_CONNECTION_TYPE = 'local'

#Returns performance of a given DFrame portfolio between dates
class PortfolioReturn(object):
    def __init__(self, portfolio, start_date, end_date):
        self.portfolio = portfolio.copy()
        self.start_date = start_date
        self.end_date = end_date

    def get_portfolio_performance(self):
        self.get_price_data()
        self.calculate_pct_chg()
        return self.calculate_return()

    #***Could have DB that stores prices on specific days
    #***multiprocess
    def get_price_data(self):
        tickers = self.portfolio['ticker']
        conn = start_db_connection(DB_CONNECTION_TYPE)
        with closing(conn.cursor()) as cur:
            for ticker in tickers:
                #price_data = self.get_db_price_data(cur, ticker)
                price_data = self.request_price_data(ticker)
                if price_data is not None and price_data.any():
                    self.portfolio.loc[self.portfolio.ticker==ticker, 'startdate'] = price_data[0]
                    self.portfolio.loc[self.portfolio.ticker==ticker, 'enddate'] = price_data[-1]
        conn.close()

    #def get_db_price_data(self, cur, ticker):
    #    cur.execute('''SELECT * date, price FROM equitypricedata WHERE
    #                ticker = %s AND (date = %s OR date = %s)''', (ticker,
    #                self.start_date, self.end_date))
    #    return cur.fetchall()

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
                                    self.end_date)['Close']
            if priceData.empty: return None
            return priceData
        except IOError:
            print 'Google Data Access for {} Failed'.format(ticker)
        return
    #def request_price_data(self, datetype, date):
    #    date = datetime.strptime(date, '%Y-%m-%d')
    #    price_func = lambda x: web.DataReader(x, 'yahoo', date).iloc[0]['Close']
    #    self.portfolio[datetype] = self.portfolio['ticker'].map(price_func)

    def calculate_pct_chg(self):
        pct_chg_func = lambda x: (x['enddate']-x['startdate'])/x['startdate']
        self.portfolio['pctchg'] = self.portfolio.apply(pct_chg_func, axis=1)

    #Call losses are 0, put losses are 0
    def calculate_return(self):
        longs = self.portfolio[self.portfolio['putcall'] == 'Long']
        calls = self.portfolio[self.portfolio['putcall'] == 'Call']
        calls.ix[calls.pctchg < 0, 'pctchg'] = 0
        puts = self.portfolio[self.portfolio['putcall'] == 'Put']
        puts.ix[puts.pctchg > 0, 'pctchg'] = 0
        total_return = 0
        for df in [longs, calls, puts]:
            total_return+= (df.ix[:,'pctchg']*df.ix[:, 'weight']).sum()
        return total_return


if __name__ == '__main__':
    portfolio = Portfolio([('1336528', 1.0)], '2014-12-31')
    #portfolio = Portfolio([('1167483', 1.0)], '2014-12-31')
    pa = PortfolioReturn(portfolio.portfolio.copy(), '2015-01-01','2015-03-31')
    portfolio_return = pa.get_portfolio_performance()
    print portfolio_return

