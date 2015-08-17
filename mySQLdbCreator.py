import MySQLdb
import keys

#***Before Final need to change keys to user choice

db = MySQLdb.connect(host = keys.sqlHost, user = keys.sqlUsername, passwd = keys.sqlPassword)
cursor = db.cursor()
cursor.execute('CREATE DATABASE IF NOT EXISTS Quarterly13Fs')
db.commit()
db.close()

db = MySQLdb.connect(host = keys.sqlHost, user = keys.sqlUsername, passwd = keys.sqlPassword, db="Quarterly13Fs")
cursor = db.cursor()
sql = '''CREATE TABLE IF NOT EXISTS 13FList (
		id INT PRIMARY KEY NOT NULL AUTO_INCREMENT UNIQUE,
		CIK VARCHAR(12) NOT NULL, 
		filingDate DATE NOT NULL, 
		accessionNunber VARCHAR(24) NOT NULL UNIQUE, 
		quarterDate DATE)
	'''
cursor.execute(sql) 

sql = '''CREATE TABLE IF NOT EXISTS 13FHoldings (
		id INT PRIMARY KEY NOT NULL AUTO_INCREMENT UNIQUE,
		accessionNunber VARCHAR(24) NOT NULL,
		nameOfIssuer VARCHAR(96) NOT NULL,
		titleOfClass VARCHAR(45),
		cusip VARCHAR(12) NOT NULL,
		value INT NOT NULL,
		sshPrnamt INT,
		sshPrnamtType VARCHAR(8),
		putCall VARCHAR(16),
		investmentDiscretion VARCHAR(8) NOT NULL,
		Sole INT,
		Shared Int,
		None Int
		)'''
cursor.execute(sql)

sql = '''CREATE TABLE IF NOT EXISTS CUSIPList (
		id INT PRIMARY KEY NOT NULL AUTO_INCREMENT UNIQUE,
		CUSIP VARCHAR(9) NOT NULL UNIQUE,
		Ticker VARCHAR(10),
		LongName VARCHAR(60),
		LastPrice DECIMAL(8,2) UNSIGNED,
		LastPriceData DATETIME,
		Shares INT(10) UNSIGNED
		)'''
cursor.execute(sql)

sql = '''CREATE TABLE IF NOT EXISTS CIKList (
		id INT PRIMARY KEY NOT NULL AUTO_INCREMENT UNIQUE,
		CIK VARCHAR(12) UNIQUE,
		firmName VARCHAR(45),
		importance INT(2)
		)'''
cursor.execute(sql)

sql = '''CREATE TABLE IF NOT EXISTS missingCUSIP (
		id INT PRIMARY KEY NOT NULL AUTO_INCREMENT UNIQUE,
		CUSIP VARCHAR(9) NOT NULL,
		accessionNunber VARCHAR(24) NOT NULL
		)'''
cursor.execute(sql)

db.commit()
db.close()


