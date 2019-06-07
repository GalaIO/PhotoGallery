# -*- coding:utf8 -*-
'''
index route.
'''
from flask import render_template, make_response, request
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
from werkzeug.utils import secure_filename
from . import main
from ..models import System
from ..models import db
from config import Config
import os
import random
from urlparse import urljoin
from urllib import quote, unquote

photo_url_prefix = "/photo/"
post_save_dir = Config.BASE_PHOTO_DIR
save_dir = Config.BASE_PHOTO_DIR

# 定义路由函数
@main.route('/', methods=['GET', 'POST'])
def index_route():
    postnames = os.listdir(post_save_dir)
    postnames = randomSample(postnames, 10)
    posts = []
    for postname in postnames:
        posts.extend(construct_posts(postname, 1))
    return render_template('index.html', posts=posts)


@main.route('/<postname>', methods=['GET', 'POST'])
def index_post(postname):
    posts = construct_posts(postname, sample_count=Config.RANDOM_COUNT)
    return render_template('index.html', posts=posts)


def construct_posts(postname, sample_count=5):
    posts = []
    post_dir = os.path.join(post_save_dir, postname)
    if not os.path.exists(post_dir) or not os.path.isdir(post_dir):
        return posts
    listdirs = os.listdir(post_dir)
    listdirs = randomSample(listdirs, sample_count=sample_count)
    for subdir in listdirs:
        post = {}
        post['user'] = postname
        post['title'] = postname + '-' + subdir
        content_dir = os.path.join(post_dir, subdir)
        if not os.path.isdir(content_dir):
            continue
        filenames = os.listdir(content_dir)
        imgs = []
        videos = []
        for filename in filenames:
            if filename.endswith('.txt'):
                with open(os.path.join(content_dir, filename)) as summary_file:
                    post['content'] = summary_file.read()
            if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.gif'):
                img = {}
                img['url'] = urlsjoin(photo_url_prefix, postname, subdir, filename)
                img['des'] = filename
                imgs.append(img)
            if filename.endswith('.mp4'):
                video = {}
                video['url'] = urlsjoin(photo_url_prefix, postname, subdir, filename)
                video['des'] = filename
                videos.append(video)
        post['imgs'] = randomSample(imgs, 10)
        post['videos'] = videos
        posts.append(post)
    return posts


def urlsjoin(base, *args):
    return base + '/'.join(args)

def randomSample(list, sample_count=5):
    list = random.sample(list, sample_count if len(list) > sample_count else len(list))
    return list

@main.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        upload_path = os.path.join(save_dir, secure_filename(f.filename))  #注意：没有的文件夹一定要先创建，不然会提示没有该路径
        f.save(upload_path)
        return redirect(url_for('upload'))
    return render_template('upload.html')


@main.route('/photo/<photo_url>', methods=['GET'])
def new(photo_url):
    if request.method == 'GET':
        if os.path.isfile(os.path.join(post_save_dir, photo_url)):
            return send_from_directory(post_save_dir, photo_url, as_attachment=True)
        abort(404)
