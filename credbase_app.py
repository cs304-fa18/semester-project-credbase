#!/usr/bin/python2.7

"""
Flask application that manages CRED database
----------------------------------------------------------------
Khonzoda Umarova & Annabel Rothschild
CS 304 - Databases 
Final Project 
October, 2018
"""


from flask import (Flask, url_for, redirect, request, render_template, session, 
                   flash, jsonify)
#import python files that do the lookup
import dbi
 
app = Flask(__name__)
app.secret_key = "a very secret phrase"
 
 
 
 
"""Home page"""
@app.route('/')
def home():
    return render_template("home_page.html", page_title="Welcome to CRED base!", login_session="Logged in as Khonzoda")
    
    
"""News source information"""    
@app.route('/source/<int:nsid>')
def newsSource(nsid):
    conn = dbi.connect('credbase')
    source = dbi.lookupNewsSource(conn, nsid)
    if source is None:
        return render_template('notfound_page.html', msg="Sorry, no news source with this ID is in the database")
    else:
        stories = dbi.getStoriesByNewsSource(conn, nsid)
        return render_template('news_source_page.html', page_title=source['name'], stories=stories)


"""User information"""
@app.route('/user/<int:uid>')
def user(uid):
    # return render_template('user_page.html', page_title="Khonzoda", sources=[{'name':'cnn.com', 'addDate':'11-28-2018'}, 
    #                                                                          {'name':'snopes.com', 'addDate':'11-28-2018'}])
    conn = dbi.connect('credbase')
    user_info = dbi.lookupUser(conn, uid)
    if len(user_info) == 0:
        return render_template('notfound_page.html', msg="Sorry, no user with this ID exists")
    else:
        sources = dbi.getWatchedNewsSources(conn, uid)
        return render_template('user_page.html', page_title=user_info['name'], sources=sources)
        
        
        
@app.route('/source/search/', defaults={'search_term':''})
@app.route('/source/search/<search_term>')
def newsSourceSearchResults(search_term):
    return render_template('searched_sources_page.html', page_title="Search results for: 'daily'", 
                            search_results=[{'name':'Daily Mail', 'url':'https://www.dailymail.co.uk'}, 
                                            {'name':'The Daily Beast', 'url':'https://www.thedailybeast.com/'}])
    # conn = dbi.connect('credbase')
    # search_results = dbi.getSearchedNewsSources(conn, search_term)
    # return render_template('searched_sources_page.html', page_title="Search results for: '" + search_term + "'", search_results=search_results)
    
        
@app.route('/search/', methods=['GET', 'POST'])
def search():
    '''Redirects to the page with news source search results'''
    search_term = request.form.get("searchterm")
    return redirect(url_for('newsSourceSearchResults', search_term=search_term))
    

#NEED TO DEFINE LOGINS & SIGNUPS
@app.route('/join/')
def signup():
    return redirect(request.referrer) 
    
@app.route('/login/', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form.get('uid')
        #return redirect(url_for('movies', serachTerm=session.get('searchTerm', '')))
        return redirect(request.referrer)     

     
if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)