from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbsetup import Base, Category, CategoryItem, User

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Web Server Project"

engine = create_engine('sqlite:///shoppingcart.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# JSON APIs
@app.route('/categories/JSON/')
def categoriesJSON():
    #category = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])

@app.route('/category/<int:category_id>/catalog/JSON/')
def catalogItemsJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    catalogItems = session.query(CategoryItem).filter_by(
        category_id=category_id).all()
    return jsonify(catalogItems=[i.serialize for i in catalogItems])

@app.route('/users/JSON/')
def userJSON():
    users = session.query(User).all()
    return jsonify(users=[u.serialize for u in users])


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    print state
    return render_template('login.html', STATE=state)

# Show homepage with all categories
@app.route('/')
@app.route('/category')
def showCategories():
    categories = session.query(Category).all()
    return render_template('home.html', categories=categories)

# Show a category's catalog
@app.route('/category/<int:category_id>')
@app.route('/category/<int:category_id>/catalog')
def showCatalog(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CategoryItem).filter_by(
        category_id=category_id).all()
    return render_template('catalog.html', items=items, category=category)

# Create a new catalog item
@app.route(
    '/category/<int:category_id>/catalog/new', methods=['GET', 'POST'])
def newCatalogItem(category_id): 
    # check if there is a user logged in. if not, redirect to login
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))       
    if request.method == 'POST':
        newItem = CategoryItem(itemName=request.form['itemName'], description=request.form[
                           'description'], price=request.form['price'], category_id=category_id, user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('showCatalog', category_id=category_id))
    else:
        return render_template('newCatalogItem.html', category_id=category_id)

# Show a catalog item's information and options to edit/delete
@app.route('/category/<int:category_id>/catalog/<int:item_id>')
def showCatalogItem(item_id, category_id):
    item = session.query(CategoryItem).filter_by(id=item_id).one()
    return render_template('viewCatalogItem.html', item_id=item_id, category_id=category_id, item=item) 

# Edit a catalog item
@app.route('/category/<int:category_id>/catalog/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editCatalogItem(category_id, item_id):
    # check if there is a user logged in. if not, redirect to login
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    editedItem = session.query(CategoryItem).filter_by(id=item_id).one()
    # check if the currently logged on user is authorized to edit this item
    if login_session['user_id'] != editedItem.user_id:
        # if the user is not authorized, give them an error message
        return "<script>function myFunction() {alert('You are not authorized to edit this item.'); window.location.href = '/category/%i/catalog/%i';}</script><body onload='myFunction()''>" % (category_id, item_id)
    if request.method == 'POST':
       if request.form['itemName']:
           editedItem.itemName = request.form['itemName']
       if request.form['description']:
           editedItem.description = request.form['description']
       if request.form['price']:
           editedItem.price = request.form['price']
       session.add(editedItem)
       session.commit()
       return redirect(url_for('showCatalog', category_id=category_id))
    else:
       return render_template(
           'editCatalogItem.html', category_id=category_id, item_id=item_id, item=editedItem)

# Delete a catalog item
@app.route('/category/<int:category_id>/catalog/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteCatalogItem(category_id, item_id):
    # check if there is a user logged in. if not, redirect to login
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    itemToDelete = session.query(CategoryItem).filter_by(id=item_id).one()
    # check if the currently logged on user is authorized to edit this item
    if login_session['user_id'] != itemToDelete.user_id:
        # if the user is not authorized, give them an error message
        return "<script>function myFunction() {alert('You are not authorized to delete this item.'); window.location.href = '/category/%i/catalog/%i';}</script><body onload='myFunction()''>" % (category_id, item_id)
    if request.method == 'POST':
       session.delete(itemToDelete)
       session.commit()
       return redirect(url_for('showCatalog', category_id=category_id))
    else:
       return render_template('deleteCatalogItem.html', category_id=category_id, item=itemToDelete)

# create a new user in the database when they log in for the first time
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

# get the email for the currently logged in user
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# gconnect uses the google log in API to authenticate a uiser
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    # see if user exists. if not, create a new one.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    
    # return some HTML to display on the webpage
    output = ''
    output += '<p>Welcome, '
    output += login_session['username']
    output += '!</p>'
    return output

# gdisconnect removes the current login session
@app.route('/gdisconnect')
def gdisconnect():
    # get the access token to verify there is currently a user logged in
    access_token = login_session.get('access_token')
    print access_token
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # if the result is good, reset the session to log the user out
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        # redirect to the homepage once the user is logged out
        return redirect(url_for('showCategories'))
    else:
        # if the token was invalid, give an error.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
    
    

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)