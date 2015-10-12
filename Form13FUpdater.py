from contextlib import closing
from dbconnection import start_db_connection
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import re
import logging
from psycopg2 import IntegrityError


#DB_CONNECTION_TYPE = 'local'
DB_CONNECTION_TYPE = 'AWS'

class Form13FUpdater(object):
    def __init__(self, cik, entries, email=False):
        self.cik = cik
        self.entries = entries

    def update_entries(self):
        if not self.entries: return
        for entry in self.entries:
            #print entry
            #ENTRIES BEFORE THIS DATE ARE TEXT
            if entry['filing_date'] < date(2013,6,30):
                continue

            link_name, quarter_date = self.get_13F_xml_location(entry['accession_nunber'])
            info_tables = self.scrape_13F(entry['accession_nunber'], link_name)
            self.upload_13f_holdings(info_tables, entry, quarter_date)

    def upload_13f_holdings(self, info_tables, entry, quarter_date):
        accession_nunber = entry['accession_nunber'].replace('-','')
        print self.cik, accession_nunber, quarter_date
        conn = start_db_connection(DB_CONNECTION_TYPE)
        with closing (conn.cursor()) as cur:
            existing_entries = self.check_for_existing_form(cur, accession_nunber)
            if existing_entries:
                cur = self.delete_existing_entries(cur, accession_nunber)
            try:
                for it in info_tables:
                    cur.execute('''INSERT INTO form13fholdings (accessionnunber,
                                nameofissuer, titleofclass, cusip, value, sshprnamt,
                                sshprnamttype, putcall, investmentdiscretion, sole,
                                shared, none) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                                %s,%s)''', (accession_nunber, it['nameOfIssuer'],
                                it['titleOfClass'], it['cusip'], it['value'],
                                it['sshPrnamt'], it['sshPrnamtType'], it['putCall'],
                                it['investmentDiscretion'], it['Sole'], it['Shared'],
                                it['None']))
                    cur = self.check_for_existing_cusip(cur, it['cusip'], accession_nunber)
                cur.execute('''INSERT INTO form13flist (cik, filingdate, accessionnunber,
                            quarterdate, updated, filingtype) VALUES (%s,%s,%s,%s,%s,%s)
                            ''', (self.cik, entry['filing_date'], accession_nunber,
                                quarter_date, entry['updated_time'],
                                entry['filing_type']))
                conn.commit()
            except IntegrityError as e:
                print 'FAILED: ' + self.cik + accession_nunber
                #***For Unique Value Vio, will also catch Null Vio, which is prob
                print e
        conn.close()

    @classmethod
    def check_for_existing_cusip(cls, cur, cusip, accession_nunber):
        cur.execute('SELECT Ticker FROM CUSIPList WHERE CUSIP = %s', (cusip,))
        if not cur.fetchall():
            tickerPair = cls.tickerLookup(cusip)
            if tickerPair:
                cur.execute('''INSERT INTO CUSIPList (cusip, ticker, longname)
                            VALUES (%s,%s,%s)''', (cusip, tickerPair[0], tickerPair[1]))
            else:
                cur.execute('''INSERT INTO missingcusip (cusip, accessionnunber)
                            VALUES (%s,%s)''', (cusip, accession_nunber))
        return cur

    @staticmethod
    def check_for_existing_form(cur, accession_nunber):
        cur.execute('''SELECT COUNT(*) as count FROM form13flist
                    WHERE accessionnunber = %s''', (accession_nunber,))
        existing_entries = cur.fetchone()[0]
        if existing_entries: return True
        else: return False

    @staticmethod
    def delete_existing_entries(cur, accession_nunber):
        cur.execute('''DELETE FROM form13Fholdings WHERE
                    accessionnunber = %s''', (accession_nunber,))
        cur.execute('''DELETE FROM form13flist WHERE
                    accessionnunber = %s''', (accession_nunber,))
        print 'exit deletion'
        return cur

    def scrape_13F(self, accession_nunber, link_name):
        form_url = ("http://www.sec.gov/Archives/edgar/data/{0}/{1}/{2}".format(
                    self.cik, accession_nunber.replace('-',''), link_name))
        soup = BeautifulSoup(requests.get(form_url).text, 'xml')
        info_table_elements = soup.findAll('infoTable')
        return self.clean_info_table_elements(info_table_elements)

    @staticmethod
    def clean_info_table_elements(info_table_elements):
        info_tables = []
        table_keys = ['nameOfIssuer',
                     'titleOfClass',
                     'cusip',
                     'value',
                     'sshPrnamt',
                     'sshPrnamtType',
                     'investmentDiscretion',
                     'Sole',
                     'Shared',
                     'None',
                     'putCall']
        for info_table_element in info_table_elements:
            info_table = {}
            for key in table_keys:
                #for putcall which doesn't always appear
                if info_table_element.find(key):
                    info_table[key] = str(info_table_element.find(key).string)
                else: info_table[key] = None
            info_tables.append(info_table)
        return info_tables

    def get_13F_xml_location(self, accession_nunber):
        page_url = ("http://www.sec.gov/Archives/edgar/data/{}/{}-"
                         "index.htm".format(self.cik, accession_nunber))

        soup = BeautifulSoup(requests.get(page_url).text, 'lxml')
        #***Very Fragile, but website is shit organizationally
        quarter_date = soup.body.findAll('div', {'class':'info'})[3].string
        #***Also Incredibly Fragile
        #finds all links, then all links containing '.xml' and the second
        information_table_links = [x.findAll('a') for x in
                                   soup.body.findAll('td', {'scope': 'row'})]
        xml_table_links = [x[0].string for x in information_table_links if
                           x and '.xml' in x[0].string ]
        if xml_table_links:
            return [str(xml_table_links[1]), quarter_date]
        else:
            return

    @staticmethod
    def tickerLookup(cusip):
        cusip_url= ("http://quotes.fidelity.com/mmnet/SymLookup.phtml?reqfor"
                   "lookup=REQUESTFORLOOKUP&productid=mmnet&isLoggedIn=mmnet&"
                   "rows=50&for=stock&by=cusip&criteria={}&submit=Search".format(
                    cusip))
        #***FRAGILE
        try:
            soup = BeautifulSoup(requests.get(cusip_url).text, 'lxml')
            long_name = soup.findAll('font', {'class':'smallfont'})[0].string
            ticker = soup.findAll('a', href=re.compile('^/webxpress/get_quote\?QUOTE_'))
            return [ticker[0].string, long_name]
        except Exception, e:
            return
