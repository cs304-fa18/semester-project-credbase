"""
Python script that connects to the database
--------------------------------------------------
Khonzoda Umarova & Annabel Rothschild
CS 304 - Databases 
Final Project 
Fall 2018
"""
import sys
import MySQLdb
import pandas as pd
import json
import os
#import dbconn2

#annabel testing:
import mediaBias_intoNS
from urlparse import urlparse
from pprint import pprint

def connect(db):
    """Establishes a connection with the
    given database"""
    # cnf = dbconn2.read_cnf()
    # cnf['db'] = db
    # conn = MySQLdb.connect(**cnf)
    #I NEED TO FIGURE OUT HOW TO DO **CNF THING
    conn = MySQLdb.connect(user='ubuntu', host='localhost',
                          passwd='',
                          db=db)
    conn.autocommit(True)
    return conn
 
 
def lookupNewsSource(conn, nsid):
    """Extracts a news source associated with the given ID. If no such
    news source exists, None is returned"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from newsSource where nsid = %s''', [nsid])
    return curs.fetchone()
   
    
def getSimilar(conn, nsid):
    """Extracts a news source associated with the given ID. If no such
    news source exists, None is returned"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from similar where nsid1 = %s or nsid2 = %s''', [nsid, nsid])
    return curs.fetchone()
    
   
def getStoriesByNewsSource(conn, nsid):   
    """Extracts stories/search results that come from the given news source"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    #NO NEED THIS IS READ ONLY
    # curs.execute('''lock tables searchresults write''')
    curs.execute('''select * from searchresults where nsid = %s''', [nsid])
    returnVal = curs.fetchall()
    # curs.execute('''unlock tables''')
    return returnVal
    
def getNewsSourceByURL(conn, url):   
    """Extracts stories/search results that come from the given news source"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    urlLike = str("%" + url + "%")
    curs.execute('''select nsid from newsSource where url like %s''', [urlLike])
    return curs.fetchone()

def findArticlesByTopic(conn, title):   
    """Extracts stories/search results that come from the given news source"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    titleLike = '%' + title + '%'
    print titleLike
    curs.execute('''select newsSource.nsid, newsSource.name, searchresults.sid, searchresults.url, searchresults.title, searchresults.resultDate, searchresults.originQuery from newsSource, searchresults where searchresults.title like %s and newsSource.nsid = searchresults.nsid''', [titleLike])
    #annabel clean this up later, debugging
    returnVal = curs.fetchall()
    print returnVal
    return returnVal
    
    
def getSearchedNewsSources(conn, searchTerm):
    """Searches the database for a news source that matches the name provided"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    pattern = '%' + searchTerm + '%'
    curs.execute('''select * from newsSource where name like %s''', [pattern])
    return curs.fetchall()

def getArticleBySid(conn, sid):
    """Searches the database for article with matching sid"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from searchresults where sid = %s''', [sid])
    #annabel was debugging using returnVal, delete later
    returnVal =  curs.fetchone()
    print returnVal
    return returnVal

#delete article from database
def deleteSearchResult(conn, sid):
    conn = connect("credbase")
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute ('''delete from searchresults where sid=%s''', [sid])
    
#delete source from database
def deleteSource(conn, nsid):
    conn = connect("credbase")
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute ('''delete from newsSource where nsid=%s''', [nsid])
    
#article update methods, separated for clarity, not necessarily efficient
def updateArticleTitle(conn, title, sid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        curs.execute('''update searchresults set title = %s where sid = %s''', [title, sid])
    except (MySQLdb.Error, MySQLdb.Warning) as error:
        print(error)
        
def updateArticleURL(conn, url, sid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        curs.execute('''update searchresults set url = %s where sid = %s''', [url, sid])
    except (MySQLdb.Error, MySQLdb.Warning) as error:
        print(error)
        
def updateArticleResultDate(conn, date, sid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        curs.execute('''update searchresults set resultDate = %s where sid = %s''', [date, sid])
    except (MySQLdb.Error, MySQLdb.Warning) as error:
        print(error)

def updateArticleOriginQuery(conn, oq, sid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        curs.execute('''update searchresults set originQuery = %s where sid = %s''', [oq, sid])
    except (MySQLdb.Error, MySQLdb.Warning) as error:
        print(error)

#update source methods, many for clarity:
#there's a way to do this with sql replace field but I can't make it work
def updateSourceName(conn, name, nsid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        curs.execute('''update newsSource set name = %s where nsid = %s''', [name, nsid])
    except (MySQLdb.Error, MySQLdb.Warning) as error:
        print(error)
        
def updateSourcePublisher(conn, publisher, nsid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        curs.execute('''update newsSource set publisher = %s where nsid = %s''', [publisher, nsid])
    except (MySQLdb.Error, MySQLdb.Warning) as error:
        print(error)
        
def updateSourceMediatype(conn, mediatype, nsid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        curs.execute('''update newsSource set mediatype = %s where nsid = %s''', [mediatype, nsid])
    except (MySQLdb.Error, MySQLdb.Warning) as error:
        print(error)
        
def updateSourceLocation(conn, location, nsid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        curs.execute('''update newsSource set location = %s where nsid = %s''', [location, nsid])
    except (MySQLdb.Error, MySQLdb.Warning) as error:
        print(error)
 
def updateSourceEditor(conn, editor, nsid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        curs.execute('''update newsSource set editor = %s where nsid = %s''', [editor, nsid])
    except (MySQLdb.Error, MySQLdb.Warning) as error:
        print(error)     
        
def updateSourceURL(conn, url, nsid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        curs.execute('''update newsSource set url = %s where nsid = %s''', [url, nsid])
    except (MySQLdb.Error, MySQLdb.Warning) as error:
        print(error)     
        

def updateSourceDOE(conn, doe, nsid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        curs.execute('''update newsSource set doe = %s where nsid = %s''', [doe, nsid])
    except (MySQLdb.Error, MySQLdb.Warning) as error:
        print(error)     

def lookupUser(conn, uid):
    """Extracts the user associated with the given ID and information about them,
    including passoword hash??"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from user where username = %s''', [uid])
    return curs.fetchone()
    
    
def getWatchedNewsSources(conn, uid): 
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from watching where username = %s''', [uid])
    return curs.fetchall()


def checkUserPass(conn, username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select hashedPWD, name from user where username = %s''',
                     [username])
    return curs.fetchone()
    
def addUser(conn, name, username, hashed):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''lock tables user write''')
    curs.execute('''select hashedPWD, name from user where username = %s''',
                     [username])
    if curs.fetchone() is not None:
        return False
    if curs.fetchone() == None:
        curs.execute('''insert into user(name,username,access,hashedPWD) values(%s,%s,'regular',%s)''',
                     [name, username, hashed])
    curs.execute('''unlock tables''')
    return True
                     
def addStory(conn, query, date, url, title, nsid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''insert into searchresults(title,originQuery,resultDate,url,nsid) values(%s,%s,%s,%s,%s)''',
                     [title, query, date, url, nsid])

def addNewsSource(conn, name, publisher, mediatype, location, editor, url, doe):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''insert into newsSource(nsid,name,publisher,mediatype,location,editor,url,doe) values(%s,%s,%s,%s,%s,%s,%s,%s)''',
                     [None, name, publisher, mediatype, location, editor, url, doe])

def addMBF(conn, tupList):
    for entry in tupList:
        curs = conn.cursor(MySQLdb.cursors.DictCursor)
        curs.execute('''insert into newsSource(nsid,name,publisher,mediatype,location,editor,url,doe) values (%s,%s,%s,%s,%s,%s,%s,%s)''',
                     [entry[0],entry[1],entry[2],entry[3],entry[4],entry[5],entry[6],entry[7]])

#file methods
def addFile(conn, nm, filename, query, date):
    # curs = conn.cursor(MySQLdb.cursors.DictCursor)
    #annabel: uncomment below line when uploading thru web interface
    #curs.execute('''insert into json(nm,filename) values (%s,%s)
    #                            on duplicate key update filename = %s''',
    #                        [nm, filename, filename])
    with open("uploads/"+filename) as data_file:
	    data = json.load(data_file)
	#crap coding but not sure how to fix -- JSON probs
    df0 = pd.DataFrame(data["page_0"])
    df1 = pd.DataFrame(data["page_1"])
    df2 = pd.DataFrame(data["page_2"])
    df3 = pd.DataFrame(data["page_3"])
    df4 = pd.DataFrame(data["page_4"])
    
    df = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

    print df
    
    conn = connect('credbase')
    #will need to do some kind of nsid matching process (if in list from media bias factcheck)
    for row, column in df.iterrows():
        #add data in form 
        title = df.iloc[row][0].encode('utf-8')
        url = df.iloc[row][1].encode('utf-8')
        potentialNSID = getNewsSourceByURL(conn, urlparse(url).netloc)
        if potentialNSID == None:
            nsid = None
        else:
            nsid = str(potentialNSID['nsid']).encode('utf-8')
        # in future want to add new news source to newsSource
        addStory(conn, query, date, url, title, nsid)

    #remove file once we've read search results from it

if __name__ == '__main__':
    conn = connect('credbase')
    returnVal = getStoriesByNewsSource(conn, 91)
    print returnVal
    #print mediaBias_intoNS.getTups()[0]
    #addMBF(conn, mediaBias_intoNS.getTups())
    # addFile(conn, 123, "Trump wall.json", "Trump wall", "2018-01-01")
    #result = getWatchedNewsSources(conn, "123")
    #print(len(result))
    #THESE ARE ALREADY ADDED
    # addFile(conn, 123, "Men women pay gap.json", "Men women pay gap", "2018-06-22")
    # addFile(conn, 123, "female Phd.json", "female Phd", "2018-08-19")
    # addFile(conn, 123, "Global warming real.json", "Global warming real", "2018-10-07")
    # addFile(conn, 123, "Big data.json", "What is daca", "2018-10-07")
    
