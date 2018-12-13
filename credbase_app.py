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
import json
import mediaBias_intoNS
#import python files that do the lookup
import dbi
import bcrypt


 

app = Flask(__name__)
app.secret_key = "a very secret phrase"
app.config['UPLOADS'] = 'uploads'

#print mediaBias_intoNS.getTups()

#workaround to load data into databse
#dbi.addMBF(dbi.connect('credbase'), mediaBias_intoNS.getTups())
 
"""Home page"""
@app.route('/')
def home():
    return render_template("home_page.html", page_title="Welcome to CredBase!", login_session=session.get('name', 'Not logged in'))

"""User information"""
@app.route('/user/<username>')
def user(username):
    try:
        # don't trust the URL; it's only there for decoration
        if 'username' in session:
            user = session['username']
            if username != user:
                flash('You are not logged in as this account. Switch accounts to proceed')
                return redirect( url_for('home') )
            conn = dbi.connect('credbase')
            user_info = dbi.lookupUser(conn, user)
            sources = dbi.getWatchedNewsSources(conn, user)
            for source in sources:
                source['name'] = dbi.lookupNewsSource(conn, source['nsid'])['name']
            return render_template('user_page.html', page_title=user_info['name'], sources=sources, login_session=session.get('name', 'Not logged in'))
        else:
            flash('You are not logged in. Please login or join')
            return redirect( url_for('home') )
    except Exception as err:
        flash('Error: '+str(err))
        return redirect( url_for('home') )

'''Allows a logged-in user to upload a new JSON file of search results'''
@app.route('/upload/', methods=["GET", "POST"])
def file_upload():
    print session
    #check that user is logged in
    if 'username' not in session:
        flash("You must be logged in to use this feature")
        return render_template("home_page.html", page_title="Welcome to CRED base!", login_session=session.get('name', 'Not logged in'))
    #if method is GET, just render the empty page
    if request.method == 'GET':
        return render_template('upload_json.html',src='',nm='', login_session=session.get('name', 'Not logged in'))
    else:
        #catch any upload errors
        try:
            #gets CRED-ID
            nm = int(request.form['nm']) # may throw error
            query = request.form['query']
            date = request.form['date']
            #make uploader give a valid date and query for use in database
            if query == '' or date == '':
                if query == '':
                    flash('You must provide the query title')
                if date == '':
                    flash('You must provide a date in format month-day-year, ex: 01-01-2018')
                return render_template('upload_json.html',src='',nm='', login_session=session.get('name', 'Not logged in'))
            f = request.files['file']
            #check to see if file is indeed a JSON file, just checks extension
            validJSON = False 
            if f.content_type == "application/json":
                validJSON = True
            else:
                flash("Upload Error: file must be of type JSON")
            if validJSON:
                filename = secure_filename('{}{}.{}'.format(nm, query, "json"))
                pathname = os.path.join(app.config['UPLOADS'],filename)
                f.save(pathname)
                flash('Upload successful')
                conn = dbi.connect('credbase')
                dbi.addFile(conn, nm, filename, query, date)
                return render_template('upload_json.html',
                                       nm=filename, login_session=session.get('name', 'Not logged in'))
            return render_template('upload_json.html',src='',nm='', login_session=session.get('name', 'Not logged in'))
        except Exception as err:
            flash('Upload failed {why}'.format(why=err))
            return render_template('upload_json.html',src='',nm='', login_session=session.get('name', 'Not logged in'))
        

"""Returns information on a news source, given NSID (news source ID)"""    
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
        #handle error that sometimes occurs, with unicode (some titles and URLs have hex characters in them)
        try:
            for story in stories:
                story['url'] = unicode(story['url'], errors='ignore')
                story['title'] = unicode(story['url'], errors='ignore')
                story['originQuery'] = unicode(story['originQuery'], errors='ignore')
                story['resultDate'] = unicode(story['resultDate'], errors='ignore')
            return render_template('news_source_page.html', page_title=unicode(source['name'], errors='ignore'), newsSource=source, stories=stories, login_session=session.get('name', 'Not logged in'))
        #sometimes have errors turning into unicode if already converted
        except TypeError: 
            return render_template('news_source_page.html', page_title=source['name'], newsSource=source, stories=stories, login_session=session.get('name', 'Not logged in'))

'''Search for a news source by name'''
@app.route('/search/', methods=['GET', 'POST'])
def search():
    query = request.form.get("searchterm")
    option = request.form.get('search-option')
    
    if option == 'source':
        return redirect(url_for('searchNewsSources', search_term=query))
    elif option == 'article':
        return redirect(url_for('searchArticles', search_term=query))
    else:
        flash("Invalid url")
        #We need to create not found page or something...
        return redirect( url_for('home') )
    
        
@app.route('/search-sources/', defaults={'search_term':''})
@app.route('/search-sources/<search_term>')
def searchNewsSources(search_term):
    """This page displays search results when there are multiple results that
    satisfy the search query. If there is only one, it redirects to the page
    of this news source. If there are none, it flashes the message"""
    conn = dbi.connect('credbase')
    search_results = dbi.getSearchedNewsSources(conn, search_term)
    for entry in search_results:
        print entry['name']
        entry['name'] = unicode(entry['name'], errors='ignore')
        
    if len(search_results) == 1:
        return redirect(url_for('newsSource', nsid=search_results[0]['nsid']))
    elif len(search_results) == 0:
        flash('Sorry, no news source with such name was found')
    return render_template('searched_sources_page.html', page_title="Search results for: '" + search_term + "'", search_results=search_results, login_session=session.get('name', 'Not logged in'))


@app.route('/search-articles/', defaults={'search_term':''})    
@app.route('/search-articles/<search_term>', methods=['GET', 'POST'])
def searchArticles(search_term):
    '''This page displays article titles whose title is like the query'''
    conn = dbi.connect('credbase') 
    print "search term: " + search_term
    articles = dbi.findArticlesByTopic(conn, search_term)
    try:
        for entry in articles:
            print entry
            entry['url'] = unicode(entry['url'], errors='ignore')
            entry['title'] = unicode(entry['title'], errors='ignore')
            entry['name'] = unicode(entry['name'], errors='ignore')
            print entry['name']
        return render_template('search_by_query.html', articles=articles, login_session=session.get('name', 'Not logged in'))
    #don't know why error happens but it does and we handle it here
    except TypeError: 
        return render_template('search_by_query.html', articles=articles, login_session=session.get('name', 'Not logged in'))
    
'''Allows logged-in user to update articles (ie members of search results)'''    
@app.route('/update-article/<int:sid>', methods=['GET', 'POST'])
def updateArticle(sid):
    #NOT THREAD SAFE -- NEED TO FIX (should be fixed now - ARR 11/11)
    if 'username' not in session:
        flash("You must be logged in to use this feature")
        return render_template("home_page.html", page_title="Welcome to CRED base!", login_session=session.get('name', 'Not logged in'))
    
    conn = dbi.connect('credbase') 
    if request.method == "GET":
        articleInfo = dbi.getArticleBySid(conn, sid)
        #handling case of hex characters in titles and URLs
        try:
            articleInfo['url'] = unicode(articleInfo['url'], errors='ignore')
            articleInfo['title'] = unicode(articleInfo['title'], errors='ignore')
            return render_template('update_article.html', articleInfo=articleInfo, login_session=session.get('name', 'Not logged in'))
        #handle case where already converted
        except TypeError:
            return render_template('update_article.html', articleInfo=articleInfo, login_session=session.get('name', 'Not logged in'))
    if request.method == "POST":
        #if user wants to delete the article 
        if 'submitDelete' in request.form:
            if 'delete' in request.form['submitDelete']: 
                print "going to delete"
                dbi.deleteSearchResult(conn, sid)
                flash("Article with SID: " + str(sid) + " was removed from the database")
                articleInfo = dbi.getArticleBySid(conn, sid)
                return render_template('update_article.html', articleInfo=[], login_session=session.get('name', 'Not logged in'))
        #if user wants to update elements of the article's entry
        if 'submitUpdate' in request.form:
            if 'update' in request.form['submitUpdate']: 
                original = dbi.getArticleBySid(conn, sid)
                #check to see that original and current values don't match before updating
                if (original['url'] != request.form['url']) and (request.form['url'] != ""):
                    dbi.updateArticleURL(conn, request.form['url'], sid)
                if (original['resultDate'] != request.form['date']) and (request.form['date'] != ""):
                    print "updating result date: " + str(request.form['date'])
                    dbi.updateArticleResultDate(conn, request.form['date'], sid)
                if (original['originQuery'] != request.form['oq']) and (request.form['oq'] != ""):
                    dbi.updateArticleOriginQuery(conn, request.form['oq'], sid)
                if (original['title'] != request.form['title']) and (request.form['title'] != ""):
                     dbi.updateArticleTitle(conn, request.form['title'], sid)
                articleInfo = dbi.getArticleBySid(conn, sid)
                return render_template('update_article.html', articleInfo=articleInfo, login_session=session.get('name', 'Not logged in'))
    articleInfo = dbi.getArticleBySid(conn, sid)
    flash("No changes made, please change appropriate values or delete item, as desired")
    return render_template('update_article.html', articleInfo=articleInfo, login_session=session.get('name', 'Not logged in'))

'''Logged-in users can update a source, to fix inaccuracies.'''
@app.route('/update-source/<int:nsid>', methods=['GET', 'POST'])
def updateSource(nsid):
    #NOT THREAD SAFE -- NEED TO FIX (should be fixed, ARR 11/11)
    if 'username' not in session:
        flash("You must be logged in to use this feature")
        return render_template("home_page.html", page_title="Welcome to CRED base!", login_session=session.get('name', 'Not logged in'))

    conn = dbi.connect('credbase') 
    if request.method == "GET":
        sourceInfo = dbi.lookupNewsSource(conn, nsid)
        #handing hex characters
        try:
            sourceInfo['url'] = unicode(sourceInfo['url'], errors='ignore')
            sourceInfo['name'] = unicode(sourceInfo['name'], errors='ignore')
            return render_template('update_source.html', sourceInfo=sourceInfo, login_session=session.get('name', 'Not logged in'))
        except TypeError:
            return render_template('update_source.html', sourceInfo=sourceInfo, login_session=session.get('name', 'Not logged in'))
    if request.method == "POST":
        print "got inside post"
        #delete if user wants
        if len(request.form) != 0:
            if 'submitDelete' in request.form:
                if 'delete' in request.form['submitDelete']: 
                    print "going to delete"
                    dbi.deleteSource(conn, nsid)
                    flash("Source with NSID: " + str(nsid) + " was removed from the database")
                    sourceInfo = dbi.lookupNewsSource(conn, nsid)
                    return render_template('update_source.html', sourceInfo=[], login_session=session.get('name', 'Not logged in'))
            #otherwise update as appropriate
            if 'submitUpdate' in request.form:
                if 'update' in request.form['submitUpdate']: 
                    original = dbi.lookupNewsSource(conn, nsid)
                    print original
                    if (original['name'] != request.form['name']) and (request.form['name'] != ""):
                         dbi.updateSourceName(conn, request.form['name'], nsid)
                    if (original['publisher'] != request.form['publisher']) and (request.form['publisher'] != ""):
                         dbi.updateSourcePublisher(conn, request.form['publisher'], nsid)
                    #special case where may not have a mediatype value picked
                    if 'mediatype' in request.form:
                        if (original['mediatype'] != request.form['mediatype']) and (request.form['mediatype'] != ""):
                             print original['mediatype']
                             print request.form['mediatype']
                             dbi.updateSourceMediatype(conn, request.form['mediatype'], nsid)
                    if (original['location'] != request.form['location']) and (request.form['location'] != ""):
                         dbi.updateSourceLocation(conn, request.form['location'], nsid)
                    if (original['editor'] != request.form['editor']) and (request.form['editor'] != ""):
                         dbi.updateSourceEditor(conn, request.form['editor'], nsid)
                    if (original['url'] != request.form['url']) and (request.form['url'] != ""):
                        dbi.updateSourceURL(conn, request.form['url'], nsid)
                    if (original['doe'] != request.form['doe']) and (request.form['doe'] != ""):
                         dbi.updateSourceDOE(conn, request.form['doe'], nsid)
                    sourceInfo = dbi.lookupNewsSource(conn, nsid)
                    return render_template('update_source.html', sourceInfo=sourceInfo, login_session=session.get('name', 'Not logged in'))
        
        else:
            print "got into else"
            print dbi.lookupNewsSource(conn, nsid)
            sourceInfo = dbi.lookupNewsSource(conn, nsid)
            try:
                sourceInfo['url'] = unicode(sourceInfo['url'], errors='ignore')
                sourceInfo['name'] = unicode(sourceInfo['name'], errors='ignore')
                return render_template('update_source.html', sourceInfo=sourceInfo, login_session=session.get('name', 'Not logged in'))
            except TypeError:
                return render_template('update_source.html', sourceInfo=sourceInfo, login_session=session.get('name', 'Not logged in'))
    flash("No changes made, please change appropriate values or delete item, as desired")
    return render_template('update_source.html', sourceInfo=sourceInfo, login_session=session.get('name', 'Not logged in'))
    
'''Logged-in users can add a new source.'''    
@app.route('/add-source/', methods=['GET', 'POST'])
def addSource():
    #NOT THREAD SAFE -- NEED TO FIX (should be fixed, ARR 11/11)
    if 'username' not in session:
        flash("You must be logged in to use this feature")
        return render_template("home_page.html", page_title="Welcome to CRED base!", login_session=session.get('name', 'Not logged in'))
    conn = dbi.connect('credbase') 
    if request.method == "GET":
        return render_template('add_source.html', login_session=session.get('name', 'Not logged in'))
    else:
        if 'submitSourceAdd' in request.form:
            print request.form
            if 'add' in request.form['submitSourceAdd']:
                #ARR: this is ugly code, might be a better way to check for None values...
                #I'll keep pondering 
                if request.form['name'] == "":
                    #only mandatory information for a source is a name
                    flash("Your source must have a name")
                    return render_template('add_source.html',login_session=session.get('name', 'Not logged in'))
                else:
                    name = request.form['name']
                if request.form['publisher'] == "":
                    publisher = None
                else:
                    publisher = request.form['publisher']
                #have to handle mediatype specially bc radio button
                if 'mediatype' not in request.form['submitSourceAdd']:
                    mediatype = None
                else:
                    mediatype = request.form['mediatype']
                if request.form['location'] == "":
                    location = None
                else:
                    location = request.form['location']
                if request.form['editor'] == "":
                    editor = None
                else:
                    editor = request.form['editor']
                if request.form['url'] == "":
                    url = None
                else:
                    url = request.form['url']
                if request.form['doe'] == "":
                    doe = None
                else:
                    doe = request.form['doe']
                dbi.addNewsSource(conn, name, publisher, mediatype, location, editor, url, doe)
                flash("New news source " + name + " was successfully added.")
                return render_template('add_source.html',login_session=session.get('name', 'Not logged in'))
                
# '''COMMENTED OUT - KHONZODA'''        
# @app.route('/delete-article/<int:sid>', methods=['GET', 'POST'])
# def deleteArticle(sid):
#     '''Redirects to the page with pre-filled information to update for article'''
#     conn = dbi.connect('credbase') 
#     return render_template('delete_article.html')

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