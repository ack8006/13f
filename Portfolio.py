import pandas as pd
from pandas import DataFrame
from GetHoldingsData import GetHoldingsData


class Portfolio(object):
    def __init__(self, members_list, quarter_date, filing_date='2200-01-01',
                 min_port_weight=0, min_underlying_weight=0, top_ideas=None):
        self.members_list = members_list
        self.quarter_date = quarter_date
        self.filing_date = filing_date
        self.min_port_weight = min_port_weight
        self.min_underlying_weight = min_underlying_weight
        self.portfolio = self.generate_portfolio()

    def generate_portfolio(self):
        portfolios = self.get_portfolios()
        portfolio = self.combine_portfolios(portfolios)
        portfolio = self.filter_min_weight(portfolio, self.min_port_weight)
        portfolio = self.update_portfolio_weights(portfolio)
        portfolio = self.drop_columns(portfolio)
        portfolio.sort(columns='weight', inplace=True, ascending=False)
        return portfolio

    def get_portfolios(self):
        portfolios = []
        for member_pair in self.members_list:
            cik, weighting = member_pair
            ghd = GetHoldingsData(cik, self.quarter_date, self.filing_date)
            portfolio = ghd.get_portfolio()
            portfolio = self.filter_min_weight(portfolio, self.min_underlying_weight)
            portfolio = self.apply_portfolio_weighting(portfolio, weighting)
            portfolios.append(portfolio)
        return portfolios

    def apply_portfolio_weighting(self, portfolio, weight):
        weight_func = lambda x: x*weight
        portfolio['weight'] = portfolio['weight'].map(weight_func)
        return portfolio

    def filter_min_weight(self, portfolio, weight):
        portfolio = portfolio.drop(portfolio[portfolio.weight <
                                    weight].index)
        #return self.update_portfolio_weights(portfolio)
        return portfolio

    def combine_portfolios(self, portfolios):
        portfolio = DataFrame()
        for port in portfolios:
            portfolio = pd.concat([portfolio, port])
        portfolio = portfolio.groupby(['ticker','nameofissuer','cusip', 'putcall']
                                      , as_index=False).sum()
        portfolio = self.update_portfolio_weights(portfolio)
        return portfolio

    def drop_columns(self, portfolio):
        return portfolio.drop(['sshprnamt','value','sole','shared','none'],
                              axis=1)

    def update_portfolio_weights(self, portfolio):
        reduced_weight= portfolio['weight'].sum(axis=0)
        weight_func = lambda x: x/float(reduced_weight)
        portfolio['weight'] = portfolio['weight'].map(weight_func)
        return portfolio

    def difference_in_holdings(self, Portfolio2Inst):
        portfolio2 = Portfolio2Inst.portfolio.copy()
        portfolio2['weight'] = portfolio2['weight']*-1
        difference = pd.concat([self.portfolio, portfolio2])
        return difference.groupby(['ticker','nameofissuer','cusip','putcall'],
                                      as_index=False).sum().sort(columns='weight',
                                                                 ascending=False)


if __name__ == '__main__':
    portfolio = Portfolio([('1336528',1.0)], '2014-12-31')
    #portfolio2 = Portfolio([('1336528',1.0)], '2014-09-30')
    #portfolio = Portfolio([('1582090',1.0)], '2014-12-31')
    #portfolio = Portfolio([('1159159',1.0)], '2014-12-31')
    #portfolio = Portfolio([('1159159',1.0)], '2014-12-31',
    #                      min_underlying_weight = 0.05)
    #portfolio = Portfolio([('1336528',0.5), ('1582090',0.5)], '2014-12-31')
    #portfolio = Portfolio([('1336528',0.5), ('1582090',0.5)], '2014-12-31',
    #                       min_port_weight=.05)

    print portfolio.portfolio
    #print portfolio2.portfolio
    #print portfolio.difference_in_holdings(portfolio2)


