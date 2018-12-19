from urlparse import urlparse
from pprint import pprint
import json
import sys
import MySQLdb
import pandas as pd
import json
from flask import (Flask, url_for, redirect, request, render_template, session, 
                   flash, jsonify)
import dbi


with open('uploads/mediabiasfactcheck_dct.json') as f:
    data = json.load(f)

tuplist = []
def getTups():
    outF = open("MBFC_all.txt", "w")
    
    conn = dbi.connect('credbase')
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
            tup = "(" + "NULL" + ", " + unicode(name, errors='ignore') + ", " + str(publisher) + ", " + str(mediatype) + ", " + str(location) + ", " + str(editor) + ", " + unicode(url, errors='ignore') + ", " + str(doe) +"), " 
        else:
            tup = "(" + "NULL" + ", " + unicode(name, errors='ignore') + ", " + str(publisher) + ", " + str(mediatype) + ", " + str(location) + ", " + str(editor) + ", " + unicode(url, errors='ignore') + ", " + str(doe) +")" 
        outF.write(tup)
        #dbi.addNewsSource(conn, name, publisher, mediatype, location, editor, url, doe)
        count += 1
        #tuplist.append(tup)
        #[count, name, publisher, mediatype, location, editor, url, doe])
    outF.close()
    #return tuplist
    
    
getTups()