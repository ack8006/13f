#from xmlScraper import UpdateChecker, Form13FUpdater
from Form13FUpdater import Form13FUpdater
from UpdateChecker import UpdateChecker
import sys
sys.path.append('../')
from dbconnection import start_db_connection
from contextlib import closing
from datetime import date
import multiprocessing as mp
#import keys
from time import sleep

#Bugs
#*******There is some request per second rate from the SEC that will
    #shut me down. so now i'm pausing between every request

#***SHOULD ONLY SELECT CIKS where last update in range of possibilities
def getCIKList():
    conn = start_db_connection('local')
    #conn = start_db_connection('AWS')
    with closing(conn.cursor()) as cur:
        cur.execute('''SELECT CIK FROM CIKList
                    WHERE importance<=3''')
        cikList = [x[0] for x in cur.fetchall()]
    conn.close()
    return cikList

#def createProcessesList(cikList):
#    processes = []
#    for cik in cikList:
#        lastDate = upCheck.mostRecentForm13F(cik)
#        print cik + ": " + str(lastDate)
#        if not lastDate or (lastDate and
#                    abs(date.today()-lastDate).days > days_for_update_check):
#            processes.append(mp.Process(target=checkAndUpdate, args=(cik, lastDate)))

def checkAndUpdate(cik):
    uc = UpdateChecker(cik)
    entries = uc.get_13F_forms_to_update()
    fu = Form13FUpdater(cik, entries)
    fu.update_entries()


if __name__ == '__main__':
    days_for_update_check = 60
    #days_for_update_check =85
    cikList = getCIKList()
    pool = mp.Pool(6)
    pool.map(checkAndUpdate, cikList)
