#!/usr/bin/env python3.8
import random
import sys

sys.path.insert(0, '../')  # 将脚本文件的上级目录添加到导包路径首位

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'PYMARA.settings'  # 指定使用的配置文件

import django

django.setup()  # 导入django，将django环境生效

from blog.models import *

user = User.objects.get(id=2)
blog = Blog.objects.get(id=1001)

count = 10
while count:
    r=random.randint(1, 5)
    count -= 1
    comment = Comment.objects.create(genre='text', blog=blog, user=user)
    CommentHistory.objects.create(text='测试评论' + str(random.randint(0, 999)), comment=comment)
    for __ in range(r):
        c_comment=Comment.objects.create(genre='text', blog=blog, user=user, parent_comment_id=comment.id,to_user_id=user.id)
        CommentHistory.objects.create(text='测试子评论' + str(random.randint(0, 999)), comment=c_comment)

