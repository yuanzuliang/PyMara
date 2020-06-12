#!/usr/bin/env python3.8

import sys

sys.path.insert(0, '../')  # 将脚本文件的上级目录添加到导包路径首位

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'PYMARA.settings'  # 指定使用的配置文件

import django

django.setup()  # 导入django，将django环境生效

import csv

from Public.tools import success
from blog.models import OtherUrl, Category, Blog, BlogHistory
from user.models import User


def add_blog_data():
    print('开始执行')
    print('要花费很长时间,请耐心等待,程序很正常...')
    print('ps:--> 懒得优化 <--')
    try:
        user = User.objects.get(id=1)
        with open('/home/littlemonster/WEB/PYMARA/blog_data.csv') as f:
            f_csv = csv.reader(f)
            for row in f_csv:
                try:
                    blog = OtherUrl.objects.get(url=row[2]).blog
                    try:
                        category = Category.objects.get(category=row[0])
                        category.blog.add(blog)
                    except:
                        Category.objects.create(category=row[0]).blog.add(blog)
                except:
                    blog = Blog.objects.create(title=row[1], abstract=row[7], original=False, is_blog=False, user=user)
                    OtherUrl.objects.create(url=row[2], blog=blog)
                    score = int(row[3]) + int(row[4]) * 10 + (int(row[6]) + int(row[5])) * 50
                    BlogHistory.objects.create(comment=row[5], favorite=row[6], browse=row[3], praise=row[4],
                                               score=score,
                                               blog=blog)
    except:
        print('你需要创建一个id为1的用户')
    print('执行完毕')


add_blog_data()
