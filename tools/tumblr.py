#!/usr/bin/env python
# coding=utf-8

import requests
import sys
import os
from bs4 import BeautifulSoup
import time
import traceback

proxies = {
  'http': 'http://127.0.0.1:1080',
  'https': 'http://127.0.0.1:1080',
}

def get_source(nickname, page_index):
    aim_main_url = "https://%s.tumblr.com" % (nickname)
    aim_url = "https://%s.tumblr.com/page/%d" % (nickname, page_index)
    tumblr_dir = nickname
    print('[o] Get source from blog %s ...' % aim_url)
    try:
        # response_string = str(open('test.txt', 'r').read())
        response_string = requests.get(url=aim_url, timeout=50).content.decode('utf8')
        soup = BeautifulSoup(response_string, 'html.parser')
        articles = soup.find_all('article')
        for count, article in enumerate(articles):
            post_body = article.find('div', attrs={"class": "post-body"})
            article_indent = getattr(post_body, 'text', "default-" + str(count))
            if len(article_indent) < 1:
                article_indent = "default-" + str(count)
            article_dirname = article_indent.strip()[:20]
            article_dirpath = os.path.join(tumblr_dir, article_dirname)
            # print 'new article in %s...' % article_dirpath
            if not os.path.exists(article_dirpath):
                os.makedirs(article_dirpath)
            with open(os.path.join(article_dirpath, u"summary.txt"), "wb") as summary_file:
                summary_file.write(article_indent.encode('utf8'))
            if post_body is not None:
                post_body_download(aim_main_url, article, article_dirpath, post_body)
            else:
                iframe_download(aim_main_url, article, article_dirpath)
        print 'finish download!'
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        # get_source(nickname, page_index)


def post_body_download(aim_main_url, article, article_dirpath, post_body):
    videos = post_body.find_all('source')
    images = post_body.find_all('img')
    print "video count=%s, image count=%s..." % (len(videos), len(images))
    if len(videos) == 0 and len(images) == 0:
        iframe_download(aim_main_url, article, article_dirpath)
    for video in videos:
        video_source = video['src']
        video_name = 'tumblr_' + video_source.split('tumblr_')[1].split('/')[0]
        write_file(video_source, article_dirpath, video_name)
    for image in images:
        image_url = image['src']
        image_name = image_url.split('/')[-1]
        write_file(image_url, article_dirpath, image_name)


def iframe_download(aim_main_url, article, article_dirpath):
    iframe_src = article.find('iframe')['src']
    if not iframe_src.startswith('http'):
        iframe_src = aim_main_url + iframe_src
    # print 'media source in %s...' % iframe_src
    # media_content = str(open('test2.txt', 'r').read())
    media_content = requests.get(url=iframe_src, timeout=50).content.decode('utf8')
    media = BeautifulSoup(media_content, 'html.parser')
    if "/video/" in iframe_src:
        video_source = media.find('source')['src']
        video_name = 'tumblr_' + video_source.split('tumblr_')[1].split('/')[0] + '.mp4'
        write_file(video_source, article_dirpath, video_name)
    else:
        images = media.find_all('a')
        for image in images:
            image_url = image['href']
            image_name = image_url.split('/')[-1]
            write_file(image_url, article_dirpath, image_name)

def write_file(source_url, dir_path, file_name):
    source_path = os.path.join(dir_path, file_name)
    if not os.path.exists(source_path):
        print('[*] Source %s is downloading' % (file_name))
        file_download = requests.get(url=source_url, timeout=50)
        if file_download.status_code == 200:
            open(source_path, 'wb').write(file_download.content)
    else:
        print('[*] Source %s has been downloaded.' % file_name)



if __name__ == '__main__':
    page_num = 65 #int(sys.argv[1])
    for index in range(1, page_num + 1):
        get_source("galaggg", index)
        time.sleep(2)


