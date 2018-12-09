#!/usr/bin/python2.7

"""
Flask application that manages CRED database
----------------------------------------------------------------
Khonzoda Umarova & Annabel Rothschild
CS 304 - Databases 
Final Project 
November, 2018
"""


from flask import (Flask, url_for, redirect, request, render_template, session, 
                   flash, jsonify)
#files -- annabel
from werkzeug import secure_filename
import os
import imghdr
import json
import mediaBias_intoNS
#import python files that do the lookup
import dbi
import bcrypt


 

app = Flask(__name__)
app.secret_key = "a very secret phrase"
app.config['UPLOADS'] = 'uploads'

dbi.addMBF(mediaBias_intoNS.getTups())
 
"""Home page"""
@app.route('/')
def home():
    return render_template("home_page.html", page_title="Welcome to CRED base!", login_session=session.get('name', 'Not logged in'))

"""User information"""
@app.route('/user/<username>')
def user(username):
    try:
        # don't trust the URL; it's only there for decoration
        if 'username' in session:
            username = session['username']
            conn = dbi.connect('credbase')
            user_info = dbi.lookupUser(conn, username)
            sources = dbi.getWatchedNewsSources(conn, username)
            return render_template('user_page.html', page_title=user_info['name'], sources=sources, login_session=session.get('name', 'Not logged in'))
        else:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('home') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('home') )


@app.route('/upload/', methods=["GET", "POST"])
def file_upload():
    if request.method == 'GET':
        return render_template('upload_json.html',src='',nm='')
    else:
        try:
            nm = int(request.form['nm']) # may throw error
            query = request.form['query']
            date = request.form['date']
            #make uploader give a valid date and query for use in database
            if query == '' or date == '':
                if query == '':
                    flash('You must provide the query title')
                if date == '':
                    flash('You must provide a date in format month-day-year, ex: 01-01-2018')
                return render_template('upload_json.html',src='',nm='')
            f = request.files['file']
            validJSON = False 
            # weak check to see if file is true json file
            if f.content_type == "application/json":
                validJSON = True
            else:
                flash("Upload Error: file must be of type JSON")
            if validJSON:
                filename = secure_filename('{}.{}'.format(nm,"json"))
                print "filename: " + filename
                pathname = os.path.join(app.config['UPLOADS'],filename)
                print "pathname: " + pathname
                f.save(pathname)
                print "saved file"
                flash('Upload successful')
                conn = dbi.connect('credbase')
                curs = conn.cursor()
                dbi.addFile(conn, nm, filename, query, date)
                return render_template('upload_json.html',
                                       src=url_for('file_upload',nm=nm),
                                       nm=nm)
            return render_template('upload_json.html',src='',nm='')
        except Exception as err:
            flash('Upload failed {why}'.format(why=err))
            return render_template('upload_json.html',src='',nm='')
        
        
@app.route('/source/search/', defaults={'search_term':''})
@app.route('/source/search/<search_term>')
def newsSourceSearchResults(search_term):
    conn = dbi.connect('credbase')
    search_results = dbi.getSearchedNewsSources(conn, search_term)
    return render_template('searched_sources_page.html', page_title="Search results for: '" + search_term + "'", search_results=search_results, login_session=session.get('name', 'Not logged in'))

    
    
    
"""News source information"""    
@app.route('/source/<int:nsid>')
def newsSource(nsid):
    conn = dbi.connect('credbase')
    source = dbi.lookupNewsSource(conn, nsid)
    if source == None:
        flash("Sorry, no news source with this ID is in the database")
        #We need to create not found page or something...
        return redirect( url_for('home') )
    else:
        stories = dbi.getStoriesByNewsSource(conn, nsid)
        return render_template('news_source_page.html', page_title=source['name'], newsSource=source, stories=stories, login_session=session.get('name', 'Not logged in'))

        
@app.route('/search/', methods=['GET', 'POST'])
def search():
    '''Redirects to the page with news source search results'''
    search_term = request.form.get("searchterm")
    return redirect(url_for('newsSourceSearchResults', search_term=search_term))
    

@app.route('/source/search/', defaults={'search_term':''})
@app.route('/source/search/<search_term>')
def newsSourceSearchResults(search_term):
    """This page displays search results when there are multiple results that
    satisfy the search query. If there is only one, it redirects to the page
    of this news source. If there are none, it flashes the message"""
    conn = dbi.connect('credbase')
    search_results = dbi.getSearchedNewsSources(conn, search_term)
    if len(search_results) == 1:
        return redirect(url_for('newsSource', nsid=search_results[0]['nsid']))
    elif len(search_results) == 0:
        flash('Sorry, no news source with such name was found')
    return render_template('searched_sources_page.html', page_title="Search results for: '" + search_term + "'", search_results=search_results, login_session=session.get('name', 'Not logged in'))
  


##-------------------# Pages for session/login management #-------------------##
@app.route('/login/', methods = ['POST'])
def login():
    try:
        username = request.form['username']
        passwd = request.form['password']
        conn = dbi.connect('credbase')
        result = dbi.checkUserPass(conn, username)
        
        if result is None:
            # Same response as wrong password, so no information about what went wrong
            flash('login incorrect. Try again or join')
            return redirect( url_for('home'))
            
        hashed = result['hashedPWD']
        name = result['name']
        # strings always come out of the database as unicode objects
        
        if bcrypt.hashpw(passwd.encode('utf-8'),hashed.encode('utf-8')) == hashed:
            flash('successfully logged in as '+username)
            session['username'] = username
            session['name'] = name
            return redirect( url_for('user', username=username) )
        else:
            flash('login incorrect. Try again or join')
            return redirect( url_for('home'))
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('home') )
        

@app.route('/logout/', methods = ['POST'])
def logout():
    try:
        if 'username' in session:
            session.pop('username')
            session.pop('name')
            flash('You are logged out')
            return redirect(url_for('home'))
        else:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('home') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('home') )


@app.route('/join/', methods = ['POST'])
def join():
    try:
        name = request.form['name']
        username = request.form['username']
        passwd1 = request.form['password1']
        passwd2 = request.form['password2']
        if passwd1 != passwd2:
            flash('passwords do not match')
            return redirect( url_for('home'))
        hashed = bcrypt.hashpw(passwd1.encode('utf-8'), bcrypt.gensalt())
        conn = dbi.connect('credbase')
        result = dbi.checkUserPass(conn, username)
        
        #NEED TO ADD THREAD SAFE MODIFICATIONS HERE
        if result is not None:
            #WE COULD USE AJAX HERE
            flash('That username is taken')
            return redirect(url_for('home'))
        else:
            #adds a new username into the system
            dbi.addUser(conn, name, username, hashed)
        
        session['username'] = username
        session['name'] = name
        return redirect( url_for('user', username=username) )
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('home') )
    
    


if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)