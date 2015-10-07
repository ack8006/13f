from contextlib import closing
from dbconnection import start_db_connection
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
#import logging

#Errors
#***Must deal with ammended 13Fs, 53417 in particular. looking at it, not only
 #is it pulling 13fs incorrectly, it's marking them as an incorrect date
#***Files were submitted as text files prior to 3Q13...shit
#***need to try/except all url calls
#***Need to implement logging
#***Should differentiate between 13F and 13F Ammendments


DB_CONNECTION_TYPE = 'local'

#This class will return forms submitted since the last check
class UpdateChecker(object):
    def __init__(self, cik, days_to_check=85):
        self.cik = cik
        self.days_to_check = days_to_check

    def get_13F_forms_to_update(self):
        self.last_date = self.get_most_recent_13f()
        print 'CIK: ' + str(self.cik) + '  LastDate: ' + str(self.last_date)
        if not self.last_date or (abs(date.today()-self.last_date).days
                                 > self.days_to_check):
            return self.get_entries_to_update()
        else:
            return

    def get_most_recent_13f(self):
        conn = start_db_connection(DB_CONNECTION_TYPE)
        with closing(conn.cursor()) as cur:
            cur.execute('''SELECT MAX(filingDate) FROM form13flist
                           WHERE CIK = %s''', (self.cik,))
            last_date = cur.fetchone()[0]
            conn.close()
        return last_date

    def get_entries_to_update(self):
        rss_url = ("http://www.sec.gov/cgi-bin/browse-edgar?action="
                   "getcompany&CIK={}&type=13f-hr&start=0&count=40&"
                   "output=atom".format(self.cik))
        soup = BeautifulSoup(requests.get(rss_url).text, "lxml")
        entry_elements= soup.find_all('entry')
        return self.prepare_entry_elements(entry_elements)

    def prepare_entry_elements(self, entry_elements):
        entries = []
        for entryEl in entry_elements:
            filing_date = entryEl.find('filing-date').string
            filing_type = entryEl.find('filing-type').string
            updated_time = entryEl.find('updated').string
            accession_nunber = entryEl.find('accession-nunber').string
            filing_date = datetime.strptime(filing_date, "%Y-%m-%d").date()
            updated_time = updated_time.replace('T', ' ')[:-6]
            updated_time = datetime.strptime(updated_time, "%Y-%m-%d %H:%M:%S")
            if (self.last_date and filing_date <= self.last_date):
                return entries
            else:
                entry = {'accession_nunber': str(accession_nunber),
                         'filing_date': filing_date,
                         'updated_time': updated_time,
                         'filing_type': filing_type}
                entries.append(entry)
                #entries.append([str(accession_nunber), filing_date,
                #                updated_time, str(filing_type)])
        return entries
