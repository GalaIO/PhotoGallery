# -*- coding: utf-8 -*-
# 
# @Author: gyj176383
# @Date: 2018/12/15
import os
import time

def clean_dir(dir, delete_all=False):
    subdirs = os.listdir(dir)
    print 'scan dir %s' % dir
    for dirname in subdirs:
        subdir = os.path.join(dir, dirname)
        if os.path.isdir(subdir):
            clean_dir(subdir, delete_all)
            continue
        # print 'scan file %s' % dirname
        if delete_all:
            os.remove(subdir)
            print 'cleaned file %s' % dirname
            continue
        if dirname.find('.') < 1 or dirname.endswith('.pnj') or dirname.endswith('_64.png'):
            os.remove(subdir)
            print 'cleaned file %s' % dirname
            continue

    subdirs = os.listdir(dir)
    if len(subdirs) < 2:
        if len(subdirs) > 0:
            clean_dir(dir, True)
            return
        os.rmdir(dir)
        print 'cleaned dir %s' % dir
    #time.sleep(2)

import sys
if __name__ == '__main__':
    dir = sys.argv[1]
    clean_dir(dir)

