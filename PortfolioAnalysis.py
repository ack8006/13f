from Portfolio import Portfolio
from PortfolioReturn import PortfolioReturn
from datetime import timedelta, date, datetime
from dbconnection import start_db_connection
from contextlib import closing

DB_CONNECTION_TYPE = 'local'

class PortfolioAnalysis(object):
    def __init__(self, members_list):
        self.members_list = members_list

    def calculate_monthly_performance(self, quarter_date, month, year):
        portfolio = Portfolio(self.members_list, quarter_date)
        previous_month_end = date(year, month, 1)-timedelta(days=1)
        current_month_end = (date(year, month,1)+timedelta(days=32)).replace(
            day=1)-timedelta(days=1)
        return PortfolioReturn(portfolio.portfolio.copy(), previous_month_end,
                               current_month_end).get_portfolio_performance()

class InvestorAnalysis(object):
    def __init__(self, members_list, min_port_weight=0, min_underlying_weight=0,
                 top_ideas = None):
        self.members_list = members_list
        self.portfolios = {}

    def get_investment_performance(self, start_date, end_date):
        portfolio_changes = self.get_portfolio_changes(start_date, end_date)
        print portfolio_changes
        self.generate_portfolios(portfolio_changes)
        return self.calculate_cumulative_performance(portfolio_changes)

    def get_portfolio_changes(self, start_date, end_date):
        conn = start_db_connection(DB_CONNECTION_TYPE)
        with closing(conn.cursor()) as cur:
            portfolio_changes = []
            for member_pair in self.members_list:
                cik = member_pair[0]
                cur.execute(("SELECT filingdate FROM form13flist WHERE filingdate"
                            "> %s AND filingdate<%s AND CIK=%s"),
                            (start_date, end_date, cik))
                changes = cur.fetchall()
                portfolio_changes += [x[0] for x in changes]
        conn.close()
        portfolio_changes = self.add_date_ends(portfolio_changes, start_date,
                                               end_date)
        return portfolio_changes

    #Adds Start and End Dates to PortfolioChanges
    @staticmethod
    def add_date_ends(portfolio_changes, start_date, end_date):
        portfolio_changes = sorted(list(set(portfolio_changes)))
        datetime_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        datetime_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        if portfolio_changes[0] > datetime_start_date:
            portfolio_changes.insert(0, datetime_start_date)
        if portfolio_changes[-1] < datetime_end_date:
            portfolio_changes.append(datetime_end_date)
        return [str(x) for x in portfolio_changes]

    def generate_portfolios(self, portfolio_changes):
        for change in portfolio_changes:
            if change not in self.portfolios:
                self.portfolios[change] = Portfolio(self.members_list,
                                                    filing_date=change).portfolio

    def calculate_cumulative_performance(self, portfolio_changes):
        perf = PortfolioReturn(self.portfolios[portfolio_changes[0]],
                                portfolio_changes[0],
                                portfolio_changes[1]).get_portfolio_performance()
        print perf
        if len(portfolio_changes) == 2:
            return perf
        else:
            perf2 = self.calculate_cumulative_performance(portfolio_changes[1:])
            return (1+perf)*(1+perf2)-1




if __name__ == '__main__':
    #pa = PortfolioAnalysis([('1336528',1.0)])
    #pa = PortfolioAnalysis([('1159159',1.0)])
    #print pa.calculate_monthly_performance('2015-06-30', 7, 2015)

    #ia = InvestorAnalysis([('1336528',1.0)])
    ia = InvestorAnalysis([('1503174',1.0)])
    #ia = InvestorAnalysis([('1336528',0.5), ('1582090',0.5)])
    #perf = ia.get_investment_performance('2014-01-01','2015-06-30')
    perf = ia.get_investment_performance('2015-07-15','2015-10-10')
    print perf

