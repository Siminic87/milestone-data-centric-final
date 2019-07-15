import os
from flask import Flask, request, render_template, Blueprint, redirect, url_for
from flask_pymongo import PyMongo
import datetime
from datetime import date, timedelta
from bson.objectid import ObjectId

from pymongo import MongoClient
from flask_paginate import Pagination, get_page_parameter, get_page_args
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user

app = Flask(__name__)

mongo = PyMongo(app)

mod = Blueprint('tips', __name__)

### Overview + Detail Page ###

@app.route('/')
# Renders summary page of all tips inc. pagination
def all_categories():
    search = False
    q = request.args.get('q')
    if q:
        search = True
    
    page = int(request.args.get('page', 1))
    per_page = 5
    offset = (page - 1) * per_page

    tips = mongo.db.tips.find().sort("upvotes", -1).limit(per_page).skip(offset)
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=mongo.db.tips.count(), search=search, record_name='tips')
    # 'page' is the default name of the page parameter, it can be customized
    # e.g. Pagination(page_parameter='p', ...)
    # or set PAGE_PARAMETER in config file
    # also likes page_parameter, you can customize for per_page_parameter
    # you can set PER_PAGE_PARAMETER in config file
    # e.g. Pagination(per_page_parameter='pp')

    datenew = str(datetime.date.today().strftime('%d %B, %Y'))

    return render_template('tips.html',
                           tips=tips,
                           pagination=pagination,
                           categories=mongo.db.categories.find(),
                           category=mongo.db.categories.find(),
                           all=mongo.db.tips.count(),
                           datenew=datenew,
                           new=mongo.db.tips.find({"date": datenew}).count())
        
@app.route('/<category>', methods=['POST','GET'])
# Renders page filtered by category incl. pagination
def sort_by_category(category):
    search = False
    q = request.args.get('q')
    if q:
        search = True
    
    page = int(request.args.get('page', 1))
    per_page = 5
    offset = (page - 1) * per_page
    
    tips=mongo.db.tips.find({"category_name" : category}).sort("upvotes", -1).limit(per_page).skip(offset)
    categories=mongo.db.categories.find()
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=mongo.db.tips.find({"category_name" : category}).count(), search=search, record_name='tips')
    
    return render_template("category.html",
    tips=tips,
    pagination=pagination,
    categories=categories,
    category=category,
    all=mongo.db.tips.find({"category_name" : category}).count(),
    new=mongo.db.tips.find({"category_name" : category,
                            "date": str(datetime.date.today().strftime('%d %B, %Y'))}).count())
    
@app.route('/detail/<tip_id>', methods=['GET'])
# Renders page for single tip
def tip_detail(tip_id):
    the_tip = mongo.db.tips.find_one({"_id": ObjectId(tip_id)})
    
    return render_template("tipdetail.html",
    all=1,
    new=mongo.db.tips.find({"date": str(datetime.date.today().strftime('%d %B, %Y'))}).count(),
    tip=the_tip)
    
### Upvoting ###

@app.route('/upvote/<tip_id>', methods=['GET'])
# Allows users to upvote tips on the summary page
def upvote(tip_id):
    mongo.db.tips.find_one_and_update(
            {'_id': ObjectId(tip_id)},
            {'$inc': {'upvotes': int(1)}}
            )
    return redirect(url_for('all_categories'))
    
@app.route('/upvote-detail/<tip_id>', methods=['GET'])
# Allows users to upvote tips on the detail page
def upvote_detail(tip_id):
    mongo.db.tips.find_one_and_update(
        {'_id': ObjectId(tip_id)},
        {'$inc': {'upvotes': int(1)}})
    return redirect(url_for('tip_detail', tip_id=tip_id))

@app.route('/upvote/<category>/<tip_id>', methods=['GET'])
# Allows users to upvote tips on the filtered summary page
def upvote_category(category, tip_id):
    mongo.db.tips.find_one_and_update(
        {'_id': ObjectId(tip_id)},
        {'$inc': {'upvotes': int(1)}})
    return redirect(url_for('sort_by_category', category=category))
    
### Downvoting ###

@app.route('/downvote/<tip_id>', methods=['GET'])
# Allows users to downvote tips on the summary page
def downvote(tip_id):
    mongo.db.tips.find_one_and_update(
        {'_id': ObjectId(tip_id)},
        {'$inc': {'upvotes': int(-1)}})
    return redirect(url_for('all_categories'))
    
@app.route('/downvote-detail/<tip_id>', methods=['GET'])
# Allows users to downvote tips on the detail page
def downvote_detail(tip_id):
    mongo.db.tips.find_one_and_update(
        {'_id': ObjectId(tip_id)},
        {'$inc': {'upvotes': int(-1)}})
    return redirect(url_for('tip_detail', tip_id=tip_id))

@app.route('/downvote/<category>/<tip_id>', methods=['GET'])
# Allows users to downvote tips on the filtered summary page
def downvote_category(category, tip_id):
    mongo.db.tips.find_one_and_update(
        {'_id': ObjectId(tip_id)},
        {'$inc': {'upvotes': int(-1)}})
    return redirect(url_for('sort_by_category', category=category))
    
### Adding, editing & deleting TIPS ###

@app.route('/add_tip')
# Renders page with form for adding new tip
@login_required
def add_tip():
    return render_template("addtip.html",
    categories=mongo.db.categories.find())
    
@app.route('/insert_tip', methods=['POST'])
# Inserts new tip in database based on entries in form
# Upvotes count set to 0
def insert_tip():
    tips = mongo.db.tips
    tips.insert_one(
        {
            'tip_name': request.form.get('tip_name'), 
            'category_name': request.form.get('category_name'), 
            'tip_description': request.form.get('tip_description'), 
            'date': request.form.get('date'), 
            'upvotes': 0
        })
    return redirect(url_for('all_categories'))
    
@app.route('/edit_tip/<tip_id>')
# Renders tips with pre-populated form for editing tip
def edit_tip(tip_id):
    the_tip = mongo.db.tips.find_one({"_id": ObjectId(tip_id)})
    all_categories = mongo.db.categories.find()
    return render_template('edittip.html', tip=the_tip, categories=all_categories)
    
@app.route('/update_tip/<tip_id>', methods=["POST"])
# Inserts updated tip into database based on form entries
# Upvote count maintained from before
def update_tip(tip_id):
    tips = mongo.db.tips
    upvotes = mongo.db.tips.find_one({'_id': ObjectId(tip_id)}, {"upvotes": True, "_id": False})
    tips.update( {'_id': ObjectId(tip_id)},
    {
        'tip_name':request.form.get('tip_name'),
        'category_name':request.form.get('category_name'),
        'tip_description': request.form.get('tip_description'),
        'date': request.form.get('date'),
        'upvotes': upvotes["upvotes"],
    })
    return redirect(url_for('all_categories'))
    
@app.route('/delete_tip/<tip_id>')
# Deletes chosen tip from database
def delete_tip(tip_id):
    mongo.db.tips.remove({'_id': ObjectId(tip_id)})
    return redirect(url_for('all_categories'))
    
### Adding, editing & deleting CATEGORIES ###

@app.route('/get_categories')
# Renders page with overview of all categories
def get_categories():
    return render_template('categories.html',
    categories=mongo.db.categories.find())
    
@app.route('/new_category')
# Renders page with empty form for creating new category
def new_category():
    return render_template('addcategory.html')
    
@app.route('/insert_category', methods=['POST'])
# Inserts new category into databse based on form entries
def insert_category():
    categories = mongo.db.categories
    category_doc = {'category_name': request.form['category_name']}
    categories.insert_one(category_doc)
    return redirect(url_for('get_categories'))
    
@app.route('/edit_category/<category_id>')
# Renders page with pre-populated form for editing chosen category
def edit_category(category_id):
    return render_template('editcategory.html',
    category=mongo.db.categories.find_one({'_id': ObjectId(category_id)}))
    
@app.route('/update_category/<category_id>', methods=['POST'])
# Inserts updated category into databse based on form entries
def update_category(category_id):
    mongo.db.categories.update(
        {'_id': ObjectId(category_id)},
        {'category_name': request.form['category_name']})
    return redirect(url_for('get_categories'))

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)