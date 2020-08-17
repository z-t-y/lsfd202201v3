"""
@author: andy zhou
Copyright(c) all rights reserved 2020
"""
# -*- coding:utf-8 -*-
from flask import (render_template, request, flash,
                   url_for, Blueprint, current_app)
from ..models import Article
from ..forms import ArticleForm
from ..extensions import db
from ..emails import send_email
from ..utils import check_article_password

articles_bp = Blueprint("articles", __name__)


@articles_bp.route('/')
@articles_bp.route('/<int:page>')
def articles(page: int=1):
    all_articles = Article().query.all()
    if all_articles:
        article = Article().query_by_id(page)
        pagination = Article.query.order_by(
            Article.timestamp.desc()).paginate(page, 1)
        return render_template('articles/articles.html',
                               this_article=article,
                               content=article.content,
                               pagination=pagination)
    flash("No Articles! Please Create one first!", "warning")
    return render_template("result.html", url=url_for("articles.new"))


@articles_bp.route('/new/', endpoint='new')
def create_article():
    form = ArticleForm()
    return render_template('articles/new.html', form=form)


@articles_bp.route('/result/', methods=['POST'], endpoint='result')
def create_article_result():
    # get values from article page
    name = request.form['name']
    password = request.form['password']
    date = request.form['date']
    title = request.form['title']
    content = request.form['content']
    # password protection
    if not (check_article_password(password)):
        flash("Wrong Password", "warning")
        return render_template('result.html', url=url_for("articles.new"))
    # commit data
    current_app.logger.info("The article was ready to commit.")
    article = Article(
        title=title, author=name, content=content, date=date
    )
    db.session.add(article)
    db.session.commit()
    # send email to 2 admins
    email_data = {
        'title': title,
        'author': name,
        'content': content
    }
    recipients = current_app.config['ADMIN_EMAIL_LIST']
    send_email(
        recipients=recipients,
        subject="A new article was added just now!",
        template="articles/article_notification",
        **email_data
    )
    flash("Success", "success")
    return render_template('result.html', url=url_for("articles.articles"))
