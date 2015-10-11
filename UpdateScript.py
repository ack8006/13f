#from xmlScraper import UpdateChecker, Form13FUpdater
from Form13FUpdater import Form13FUpdater
from UpdateChecker import UpdateChecker
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
    with closing(conn.cursor()) as cur:
        cur.execute("SELECT CIK FROM CIKList")
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
    #DAYS_TO_CHECK_FOR_UPDATES = 82
    days_for_update_check =85
    cikList = getCIKList()
    processes = []
    for cik in cikList:
        processes.append(mp.Process(target=checkAndUpdate, args=(cik,)))
    for p in processes:
        p.start()
        #sleep(0.75)



#processes = []
#for cik in cikList:
#	lastDate = upCheck.mostRecentForm13F(cik)
#	print cik + ": " + str(lastDate)
#	if not lastDate or (lastDate and abs(date.today()-lastDate).days > DAYS_TO_CHECK_FOR_UPDATES):
#		processes.append(mp.Process(target=checkAndUpdate, args=(cik, lastDate)))
#
#for p in processes:
#	p.start()
#	#slows shit down so that not massively overloading SEC.  There is some SEC requests per second
#	#this seems to be fixing things, but it is not like i'm only hitting evry 500ms instead, this adds a new process
#	#which starts a whole new list of numbers.  only really important on first loads, after that, assuming this is
#	#run regularly, should only be a few each time.
#	sleep(0.75)
#
