from urlparse import urlparse
from pprint import pprint
import json
import sys
import MySQLdb
import pandas as pd
import json
from flask import (Flask, url_for, redirect, request, render_template, session, 
                   flash, jsonify)

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

with open('uploads/mediabiasfactcheck_dct.json') as f:
    data = json.load(f)

tuplist = []
def getTups():
    outF = open("MBFC_all.txt", "w")
    
    conn = connect('credbase')
    #substitute for NSID
    count = 0
    for entry in data:
        name = "'"+entry['name'].encode('utf-8')+"'"
        publisher = "NULL"
        mediatype = "NULL"
        location = "NULL"
        editor = "NULL"
        if entry['external_url'] != None:
            url = "'"+entry['external_url'].encode('utf-8')+"'"
        else:
            url = "NULL"
        doe = "NULL"
        if entry != data[-1]:
            tup = "(" + "NULL" + ", " + str(name) + ", " + str(publisher) + ", " + str(mediatype) + ", " + str(location) + ", " + str(editor) + ", " + str(url) + ", " + str(doe) +"), " 
        else:
            tup = "(" + "NULL" + ", " + str(name) + ", " + str(publisher) + ", " + str(mediatype) + ", " + str(location) + ", " + str(editor) + ", " + str(url) + ", " + str(doe) +")" 
        outF.write(tup)
        #dbi.addNewsSource(conn, name, publisher, mediatype, location, editor, url, doe)
        count += 1
        #tuplist.append(tup)
        #[count, name, publisher, mediatype, location, editor, url, doe])
    outF.close()
    #return tuplist
    
    
getTups()