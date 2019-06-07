#!/usr/bin/env python
# coding=utf-8

import requests
import sys
import os
from bs4 import BeautifulSoup
import time
import traceback
import re

zz = re.compile('[/\\\ \r\n\t]')

def get_source(nickname, post_name, page_index):
    aim_main_url = "https://%s.tumblr.com" % (nickname)
    aim_url = "https://%s.tumblr.com/page/%d" % (nickname, page_index)
    tumblr_dir = nickname + '-' + post_name
    save_count = 0
    print('[o] Get source from blog %s ...' % aim_url)
    try:
        # response_string = str(open('test.txt', 'r').read())
        response_string = wapper_get(aim_url)
        soup = BeautifulSoup(response_string, 'html.parser')
        articles = soup.find_all('article')
        # post_contents = soup.find_all('div', attrs={"class": "post-content"})
        # iframes = soup.find_all('iframe')
        for count, article in enumerate(articles):
            global_count = page_index * 10000 + count
            post_content = article.find(class_="post-content")
            article_indent = "default-" + str(global_count)
            if post_content is not None:
                body_text = post_content.find(class_="body-text")
                if body_text is None:
                    body_text = post_content.find(class_="post-body")
                    if body_text is None:
                        body_text = post_content
                article_indent = getattr(body_text, 'text', "default-" + str(global_count))
                article_indent = article_indent.strip()
                if len(article_indent) < 1:
                    article_indent = "default-" + str(global_count)
            article_dirname = zz.sub('', article_indent[:20])
            article_dirpath = os.path.join(tumblr_dir, article_dirname)
            # print 'new article in %s...' % article_dirpath
            if not os.path.exists(article_dirpath):
                os.makedirs(article_dirpath)
            with open(os.path.join(article_dirpath, u"summary.txt"), "wb") as summary_file:
                summary_file.write(article_indent.encode('utf8'))
            if post_content is not None:
                post_body_download(aim_main_url, article, article_dirpath, post_content)
            else:
                iframe_download(aim_main_url, article, article_dirpath)
            save_count += 1
        print 'finish download!'
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        # get_source(nickname, page_index)
    return save_count


def wapper_get(aim_url):
    return requests.get(url=aim_url, timeout=50).content.decode('utf8')


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
    try:
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
    except:
        print(traceback.format_exc())
        print('[e] iframe extra error' % (aim_main_url))

def write_file(source_url, dir_path, file_name):
    source_path = os.path.join(dir_path, file_name)
    if not os.path.exists(source_path):
        print('[*] Source %s is downloading' % (file_name))
        file_download = requests.get(url=source_url, timeout=50)
        if file_download.status_code == 200:
            open(source_path, 'wb').write(file_download.content)
    else:
        print('[*] Source %s has been downloaded.' % file_name)



def parse_following_page(nickname, page_num):
    url = "https://%s.tumblr.com/following/page/%s" % (nickname, page_num)
    print('[+] request new page %s' % (url))
    page = wapper_get(url)
    # page = str(open("followpage.txt", 'r').read())
    # page = '<html><div class="blog-card"><span class="blog-name ver">lllll</span></div></html>'
    soup = BeautifulSoup(page, 'html.parser')
    cards = soup.find_all('div', class_='blog-card')
    for card in cards:
        try:
            blog_name = card.find(class_='blog-name').text.strip()
            title = card.find(class_='title')
            if title is not None:
                title = title.text.strip()
            else:
                title = 'default'
            print('[+] find a new post page, with %s' % (blog_name))
            scrawl_articles_by_page(blog_name, title)
        except:
            print(traceback.format_exc())
            print('[--] pass the card with %s' % (blog_name))
    return len(cards)


def scrawl_articles_by_page(blog_name, post_name, page_count=5):
    tumblr_dir = blog_name + '-' + post_name
    if os.path.exists(tumblr_dir):
        print('[-] pass with %s' % (blog_name))
        return 0
    for index in range(1, page_count + 1):
        save_count = get_source(blog_name, post_name, index)
        time.sleep(3)
        # try again
        if save_count < 1 and get_source(blog_name, post_name, index) < 1 and get_source(blog_name, post_name, index) < 1:
            break

import sys
if __name__ == '__main__':
    if len(sys.argv) > 1:
        nickname = sys.argv[1]
        scrawl_articles_by_page(nickname, '')
    else:
        page_count = 25
        nickname = "galaggg"
        for index in range(20, page_count + 1):
            count = parse_following_page(nickname, index)
            time.sleep(3)
            if count < 1 and parse_following_page(nickname, index) < 1 and parse_following_page(nickname, index) < 1:
                break


