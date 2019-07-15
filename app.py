import os
from flask import Flask, request, render_template, Blueprint
from flask_pymongo import PyMongo
import datetime
from datetime import date, timedelta

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

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)