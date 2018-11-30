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
# import dbconn2

def connect(db):
    """Establishes a connection with the
    given database"""
    # cnf = dbconn2.read_cnf()
    # cnf['db'] = db
    # conn = MySQLdb.connect(**cnf)
    #I NEED TO FIGURE OUT HOW TO DO **CNF THING
    conn = MySQLdb.connect(host='localhost',
                          user='kumarova',
                          passwd='',
                          db=db)
    conn.autocommit(True)
    return conn
 
 
def lookupNewsSource(conn, nsid):
    """Extracts a news source associated with the given ID. If no such
    news source exists, None is returned"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''QUERY TO GET NEWS SOURCE HERE''', [nsid])
    return curs.fetchone()
    
   
def getStoriesByNewsSource(conn, nsid):   
    """Extracts stories/search results that come from the given news source"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''QUERY TO GET SEARCH RESULTS FOR THIS SOURCE HERE''')
    return curs.fetchall()
    
    
def getSearchedNewsSources(conn, searchTerm):
    """Searches the database for a news source that matches the name provided"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    pattern = '%' + searchTerm + '%'
    curs.execute('''QUERY TO SEARCH FOR NEWS SOURCE HERE''', [pattern])
    return curs.fetchall()


def lookupUser(conn, uid):
    """Extracts information about the user associated with the given ID. This
    includes their name, access level (admin vs standard), and the list of news
    sources the user is watching"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''QUERY TO GET USER INFO AND SOURCES THEY ARE WATCHING''', [uid])
    return curs.fetchall()

if __name__ == '__main__':
    conn = getConn('credbase')
    
    
    

