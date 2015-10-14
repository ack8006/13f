import sys
sys.path.append('../')
from dbconnection import start_db_connection
from contextlib import closing
import requests
from bs4 import BeautifulSoup
import re

DB_CONNECTION_TYPE = 'local'
#DB_CONNECTION_TYPE = 'AWS'

#http://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=13F&start=1&count=100&output=atom

#***NEEDS TO BE AFTER QUARTER END NOT AFTER LAST DATE
class LatestFilingsChecker(object):
    def __init__(self, filing_type):
        self.filing_type = filing_type

    def analyze_most_recent_filings(self):
        self.entry_elements = self.get_most_recent_filings()
        self.parse_entries()

    def get_most_recent_filings(self, start=1, count=40):
        url = ("http://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent"
               "&type={}&start={}&count={}&output=atom".format(
                   self.filing_type, start, count))
        soup = BeautifulSoup(requests.get(url).text, 'lxml')
        entry_elements = soup.find_all('entry')
        #if len(entry_elements) == count:
        #    start+=count
        #    addtional_elements = self.get_most_recent_filings(start)
        #    entry_elements += addtional_elements
        return entry_elements

    def parse_entries(self):
        conn = start_db_connection(DB_CONNECTION_TYPE)
        with closing(conn.cursor()) as cur:
            for entry in self.entry_elements:
                cik, name = self.parse_entry(entry)
                cur = self.add_to_database(cur, cik, name)
        conn.commit()
        conn.close()

    def parse_entry(self, entry):
        name_half = entry.title.string.split(' - ')[1]
        matches = re.findall('\((.*?)\)', name_half)
        while len(matches) >2:
            matches.pop(0)
        cik = str(matches[0])
        for match in matches:
            name_half = name_half.replace('('+str(match)+')', '')
        return cik, name_half

    def add_to_database(self, cur, cik, name):
        cik = str(int(cik))
        cur.execute('''SELECT * FROM ciklist WHERE cik = %s''', (cik,))
        if not cur.fetchall():
            cur.execute('''INSERT INTO ciklist (cik, firmname, importance)
                        VALUES (%s,%s,4)''', (cik, name))
        return cur


if __name__ == '__main__':
    LatestFilingsChecker('13F').analyze_most_recent_filings()







