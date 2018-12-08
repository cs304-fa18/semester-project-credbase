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
    curs.execute('''select * from searchresults where nsid = %s''', [nsid])
    return curs.fetchall()
    
    
def getSearchedNewsSources(conn, searchTerm):
    """Searches the database for a news source that matches the name provided"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    pattern = '%' + searchTerm + '%'
    curs.execute('''select * from newsSource where name like %s''', [pattern])
    return curs.fetchall()


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
    curs.execute('''insert into user(name,username,access,hashedPWD) values(%s,%s,'regular',%s)''',
                     [name, username, hashed])

if __name__ == '__main__':
    conn = connect('credbase')
    result = getWatchedNewsSources(conn, "123")
    print(len(result))
    
    
