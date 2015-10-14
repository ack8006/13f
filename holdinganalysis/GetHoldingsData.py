import pandas as pd
import numpy as np
from pandas import DataFrame
import sys
sys.path.append('../')
from dbconnection import *
from contextlib import closing
from operator import itemgetter


DB_CONNECTION_TYPE = 'local'

class GetHoldingsData(object):
    #def __init__(self, cik, quarter_date = None, filing_date = '2200-01-01'):
    def __init__(self, cik, quarter_date = None, filing_date = None):
        self.cik = cik
        if not quarter_date and not filing_date:
            raise TypeError('must include at least quarter_date or filing_date')
        self.quarter_date = quarter_date
        self.filing_date = filing_date

    def get_portfolio(self):
        self.form_list = self.get_forms()
        self.parse_form_list()
        #[filingdate, accession, type, quarterdate]
        self.pull_holdings()
        self.get_portfolio_weights()
        self.clean_putcall_values()
        return self.holdings

    def clean_putcall_values(self):
        self.holdings['putcall'] = self.holdings['putcall'].fillna(value='Long')

    def get_forms(self):
        sql_query, sql_parameters = self.generate_sql_query()
        conn = start_db_connection(DB_CONNECTION_TYPE)
        with closing(conn.cursor()) as cur:
            cur.execute(sql_query, sql_parameters)
            form_list = cur.fetchall()
        conn.close()
        return form_list

    def generate_sql_query(self):
        sql_query = '''SELECT filingdate, accessionnunber, filingtype, quarterdate
                       FROM form13flist WHERE cik=%s'''
        parameters = [self.cik]
        if self.quarter_date:
            sql_query += ' and quarterdate = %s'
            parameters.append(self.quarter_date)
        if self.filing_date:
            sql_query += ' and filingdate <= %s'
            parameters.append(self.filing_date)
        return sql_query, tuple(parameters)

    def parse_form_list(self):
        if not self.quarter_date:
            no_ammendments = [x for x in self.form_list if x[2] == '13F-HR']
            self.quarter_date = max(no_ammendments, key=itemgetter(3))[3]
            self.form_list = [x for x in self.form_list if x[3] == self.quarter_date]
        #Top sort is only important when 13F and 13F-A are on the same day
        #which happened 1503174, 2015-5-15
        self.form_list.sort(key=lambda x: x[2])
        self.form_list.sort(key=lambda x: x[0])

    def pull_holdings(self):
        sql_fields = ("CUSIPList.Ticker, {0}.CUSIP, {0}.nameOfIssuer,"
                    "{0}.titleOfClass, {0}.value, {0}.sshPrnamt,{0}.sshPrnamtType,"
                    "{0}.putCall,{0}.investmentDiscretion, {0}.Sole, {0}.Shared,"
                    "{0}.None".format('form13fholdings',))
        sql_query = '''SELECT {} from cusiplist INNER JOIN form13fholdings
                    ON cusiplist.cusip=form13fholdings.cusip WHERE
                    form13fholdings.accessionnunber = %(an)s'''.format(sql_fields)

        engine = start_engine(DB_CONNECTION_TYPE)
        self.holdings = DataFrame([])
        for form in self.form_list:
            accession_nunber = form[1]
            df = pd.read_sql_query(sql_query, engine,
                                   params={'an':accession_nunber})
            if self.holdings.empty and form[2] == '13F-HR':
                self.holdings = df
            elif self.holdings.any and form[2] == '13F-HR/A':
                self.incorporate_ammendment(df)
            else:
                raise Exception('Not supposed to be here Holdinganalysis')

    #Logic is that if ammendment has new stuff add it on, otherwise replace
    #existing entry.
    def incorporate_ammendment(self, ammendment):
        self.holdings = pd.concat([self.holdings, ammendment])
        #since take_last==True will keep the ammendment values
        self.holdings.drop_duplicates(subset=['ticker','putcall'],
                                      take_last=True, inplace=True)

    def get_portfolio_weights(self):
        total_weight = self.holdings['value'].sum(axis=0)
        weight_func = lambda x: x/float(total_weight)
        self.holdings['weight'] = self.holdings['value'].map(weight_func)


if __name__ == '__main__':
    #gd = GetHoldingsData('1159159', '2014-12-31')
    #gd = GetHoldingsData('1582090', quarter_date='2014-12-31')
    #gd = GetHoldingsData('1159159', filing_date='2015-05-14')
    gd = GetHoldingsData('1336528', filing_date='2015-02-16')

    print gd.get_portfolio()

