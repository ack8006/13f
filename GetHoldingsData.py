import pandas as pd
import numpy as np
from pandas import DataFrame
from dbconnection import *
from contextlib import closing


DB_CONNECTION_TYPE = 'local'

class GetHoldingsData(object):
    def __init__(self, cik, quarter_date, filing_date = '2200-01-01'):
        self.cik = cik
        self.quarter_date = quarter_date
        self.filing_date = filing_date

    def get_portfolio(self):
        self.form_list= self.get_forms()
        #to help deal with ammends
        self.form_list.sort(key=lambda x: x[0])
        #[filingdate, accession, type]
        self.pull_holdings()
        self.get_portfolio_weights()
        self.clean_putcall_values()
        return self.holdings

    def clean_putcall_values(self):
        self.holdings['putcall'] = self.holdings['putcall'].fillna(value='Long')

    def get_forms(self):
        conn = start_db_connection(DB_CONNECTION_TYPE)
        with closing(conn.cursor()) as cur:
            cur.execute('''SELECT filingdate, accessionnunber, filingtype FROM
                        form13flist WHERE cik=%s and quarterdate=%s and
                        filingdate <= %s''',
                        (self.cik, self.quarter_date, self.filing_date))

            form_list = cur.fetchall()
        conn.close()
        return form_list

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
    gd = GetHoldingsData('1582090', '2014-12-31')
    gd.get_portfolio()
