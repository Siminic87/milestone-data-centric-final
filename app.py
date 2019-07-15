import os
from flask import Flask, request, render_template, Blueprint, redirect, url_for
from flask_pymongo import PyMongo
import datetime
from datetime import date, timedelta
from bson.objectid import ObjectId

from pymongo import MongoClient
from flask_paginate import Pagination, get_page_parameter, get_page_args

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

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)