# coding=utf-8

import os

from flask import Flask, render_template, redirect, request, url_for
from flask import send_from_directory

from page_info import PageInfo


# get all variables
p_info = PageInfo()
TOPIC_DICT = p_info.get_topic()
CAT_DICT = p_info.get_cat()
LATEST_PAGE = p_info.get_latest_page()


app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template("base/home.html",
                            TOPIC_DICT=TOPIC_DICT,
                            LATEST_PAGE=LATEST_PAGE)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='images/favicon.ico')


@app.route('/<cat>')
def cat(cat):
    sub_cats = CAT_DICT[cat]
    return render_template("base/categories_base.html",
                           TOPIC_DICT=TOPIC_DICT,
                           cat=cat,
                           sub_cats=sub_cats)


@app.route('/<cat1>/<cat2>')
def sub_content(cat1, cat2):
    sub_cats = CAT_DICT[cat1]
    return render_template("base/sub_categories_base.html",
                           TOPIC_DICT=TOPIC_DICT,
                           uri_subcat=cat2,
                           cat=cat1,
                           sub_cats=sub_cats)


@app.route('/<cat1>/<cat2>/<topic>.html')
def content(cat1, cat2, topic):
    topic = topic + ".html"
    page = '/'.join([cat1, cat2, topic])
    sub_cats = CAT_DICT[cat1]
    return render_template(page,
                           TOPIC_DICT=TOPIC_DICT,
                           uri_subcat=cat2,
                           cat=cat1,
                           sub_cats=sub_cats)


@app.route('/contact')
def contact():
    return render_template("base/contact.html",
                           TOPIC_DICT=TOPIC_DICT)
