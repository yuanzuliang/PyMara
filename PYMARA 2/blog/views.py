import datetime
import json
import os
import time

import redis
from django.conf import settings
from django.db import transaction
from django.db.models import F, Count
from django.http import JsonResponse

from django.views import View, generic
from Public.configs import MDConfig
from Public.publictoken import logging_check, user_check
from Public.tools import success, error
from blog.models import *
from Public.update_blog_history import UpdateBlogHistory

# redis 9库 储存blog信息
r9 = redis.Redis(db=9, decode_responses=True)
# redis 10库 储存rank缓存
r10 = redis.Redis(db=10, decode_responses=True)
update = UpdateBlogHistory()
# TODO 此处获取default配置，当用户设置了其他配置时，此处无效，需要进一步完善
MDEDITOR_CONFIGS = MDConfig('default')


class Search(View):
    def get(self, request):
        keyword = request.GET.get('keyword')
        category = request.GET.get('category')
        if category == 'all':
            category = ''
        sort = request.GET.get('sort')
        # 类别搜索和排序方式
        try:
            if keyword and category and sort:
                blog_ids = Category.objects.filter(category=category)[0].blog.filter(title__icontains=keyword,
                                                                                     is_show=1,
                                                                                     status=1).extra(
                    tables=['blog_blog', 'blog_bloghistory'], where=['blog_blog.id=blog_bloghistory.blog_id'],
                    order_by=['-blog_bloghistory.{}'.format(sort)]).values_list('id', flat=True)
                return success(list(blog_ids))
                # 类别搜索
            elif keyword and category:
                blog_ids = Category.objects.filter(category=category)[0].blog.filter(title__icontains=keyword,
                                                                                     is_show=1,
                                                                                     status=1).extra(
                    tables=['blog_blog', 'blog_bloghistory'], where=['blog_blog.id=blog_bloghistory.blog_id'],
                    order_by=['-blog_bloghistory.score']).values_list('id', flat=True)
                return success(list(blog_ids))
            # 类别搜索
            elif keyword and sort:
                blog_ids = Blog.objects.filter(title__icontains=keyword, is_show=1, status=1).extra(
                    tables=['blog_blog', 'blog_bloghistory'], where=['blog_blog.id=blog_bloghistory.blog_id'],
                    order_by=['-blog_bloghistory.{}'.format(sort)]).values_list('id', flat=True)
                return success(list(blog_ids))
            # 关键字搜索
            elif keyword:
                # 查询所有符合条件的博客id按分数降序排列  高->底
                blog_ids = Blog.objects.filter(title__icontains=keyword, is_show=1, status=1).extra(
                    tables=['blog_blog', 'blog_bloghistory'], where=['blog_blog.id=blog_bloghistory.blog_id'],
                    order_by=['-blog_bloghistory.score']).values_list('id', flat=True)
                print(blog_ids)
                return success(list(blog_ids))
            else:
                raise
        except:
            return error(400, '参数错误')

    def post(self, request):
        blog_ids = json.loads(request.body).get('blog_ids')
        return success(update.get_blog_info(blog_ids))


class Rank(View):
    def get(self, request, type, page):
        if int(page) < 0 or int(page) > 90:
            return error(400, '页面数错误')
        if type == 'original':
            return success(self.get_blog_info('original', page))
        if type == 'default':
            return success(self.get_blog_info('default', page))
        if type == 'hot':
            return success(self.get_blog_info('hot', page))
        if type == 'featured':
            blog_list = self.get_featured_info(page)
            if blog_list:
                return success(blog_list)
            return error(404, '推荐已经看完了')
        return error(400, '排行榜类型错误')

    def get_original(self):
        # 原创排行
        blog_ids = Blog.objects.filter(original=True, status='1', is_show=True).extra(
            tables=['blog_blog', 'blog_bloghistory'], where=['blog_blog.id=blog_bloghistory.blog_id'],
            order_by=['-blog_bloghistory.score', '-blog_bloghistory.browse', '-blog_bloghistory.praise',
                      '-blog_bloghistory.comment'], ).values_list('id', flat=True)[:100]
        return list(blog_ids)

    def get_default(self):
        # 全站排行
        blog_ids = Blog.objects.filter(status='1', is_show=True).extra(
            tables=['blog_blog', 'blog_bloghistory'], where=['blog_blog.id=blog_bloghistory.blog_id'],
            order_by=['-blog_bloghistory.score', '-blog_bloghistory.browse', '-blog_bloghistory.praise',
                      '-blog_bloghistory.comment'], ).values_list('id', flat=True)[:100]
        return list(blog_ids)

    def get_hot(self):
        # 热门排行
        return list(r9.smembers(settings.RANK_HOT_KEY))

    def get_blog_info(self, type, page):
        res_list = []
        if not r10.exists('rank_update_time'):
            # 排行榜更新
            # 当前 时间
            m, s = time.strftime('%M-%S').split('-')
            # 距离下个整点秒数
            t = 3600 - int(m) * 60 - int(s)
            with r10.pipeline(transaction=True) as pipe:
                pipe.multi()
                # 清库
                r10.flushdb()
                # 标记更新时间
                r10.set('rank_update_time', time.strftime("%Y-%m-%d %H:%M:%S"), ex=t)
                # 更新mysql数据
                update.update_mysql()
                # 获取最新排行
                rank_default = self.get_default()
                rank_original = self.get_original()
                rank_hot = self.get_hot()
                # 缓存排行列表
                for item in rank_default[::-1]:
                    r10.lpush('rank_default', item)
                for item in rank_original[::-1]:
                    r10.lpush('rank_original', item)
                for item in rank_hot[::-1]:
                    r10.lpush('rank_hot', item)
                # 获取三个榜单的所有博客信息
                blog_list = update.get_blog_info(rank_default + rank_original + rank_hot)
                # 更新榜单缓存信息
                for blog in blog_list:
                    r10.hset(settings.BLOG_INFO_KEY + str(blog['id']), mapping=blog)
                pipe.execute()
        blog_ids = r10.lrange('rank_' + type, page, int(page) + 9)
        for blog_id in blog_ids:
            res_list.append(r10.hgetall(settings.BLOG_INFO_KEY + str(blog_id)))
        return res_list

    def get_featured_info(self, page):
        page = page * 10
        # 推荐位专用函数
        if not r9.exists('featured_ids_set'):
            with r9.pipeline(transaction=True) as pipe:
                pipe.multi()
                r9.delete('featured_ids')
                blog_ids = Blog.objects.filter(is_blog=True, is_show=True, status=1, original=True).order_by(
                    '-create_time').values_list('id', flat=True)[:100]
                for blog_id in blog_ids:
                    if r9.sadd('featured_ids_set', blog_id):
                        r9.lpush('featured_ids', blog_id)
                blog_ids = BlogHistory.objects.filter(blog__is_show=True, blog__status=1, ).order_by(
                    '-score').values_list('id', flat=True)[:100]
                for blog_id in blog_ids:
                    if r9.sadd('featured_ids_set', blog_id):
                        r9.rpush('featured_ids', blog_id)
                blog_ids = r9.zrange(settings.BLOG_CACHE_IDS_KEY, 0, -1)
                for blog_id in blog_ids:
                    if r9.sadd('featured_ids_set', blog_id):
                        r9.rpush('featured_ids', blog_id)
                r9.expire('featured_ids_set', 3600 * 24)
        print(r9.llen('featured_ids'))
        if r9.llen('featured_ids') < page:
            return False
        blog_ids = r9.lrange('featured_ids', page, page + 9)
        return update.get_blog_info(blog_ids)


class Image(generic.View):
    """ upload image file """

    # @method_decorator(csrf_exempt)

    def post(self, request, *args, **kwargs):
        upload_image = request.FILES.get("editormd-image-file", None)
        media_root = settings.MEDIA_ROOT

        # image none check
        if not upload_image:
            return JsonResponse({
                'success': 0,
                'message': "未获取到要上传的图片",
                'url': ""
            })

        # image format check
        file_name_list = upload_image.name.split('.')
        file_extension = file_name_list.pop(-1)
        file_name = '.'.join(file_name_list)
        if file_extension not in MDEDITOR_CONFIGS['upload_image_formats']:
            return JsonResponse({
                'success': 0,
                'message': "上传图片格式错误，允许上传图片格式为：%s" % ','.join(
                    MDEDITOR_CONFIGS['upload_image_formats']),
                'url': ""
            })

        # image floder check
        file_path = os.path.join(media_root, MDEDITOR_CONFIGS['image_folder'])
        if not os.path.exists(file_path):
            try:
                os.makedirs(file_path)
            except Exception as err:
                return JsonResponse({
                    'success': 0,
                    'message': "上传失败：%s" % str(err),
                    'url': ""
                })

        # save image
        file_full_name = '%s_%s.%s' % (file_name,
                                       '{0:%Y%m%d%H%M%S%f}'.format(datetime.datetime.now()),
                                       file_extension)
        with open(os.path.join(file_path, file_full_name), 'wb+') as file:
            for chunk in upload_image.chunks():
                file.write(chunk)

        return JsonResponse({'success': 1,
                             'message': "上传成功！",
                             'url': os.path.join(settings.MEDIA_URL,
                                                 MDEDITOR_CONFIGS['image_folder'],
                                                 file_full_name)})


class Editor(View):
    """
    编辑页面
    """

    @logging_check
    def post(self, request):
        # 修改为json
        obj = json.loads(request.body)
        content = obj.get('content')  # 博客正文
        title = obj.get('title')  # 博客标题
        abstract = obj.get('abstract')  # 摘要
        # 需要一个列表
        category = obj.get('category')  # 分类列表
        type = obj.get('blog_type')  # 博客状态类型
        # 数据处理

        if not content or not title or not abstract or not category or not type:
            return error(701, "博客内容不完整")

        if len(abstract) > 96:
            return error(400, '摘要超过长度')

        with transaction.atomic():
            try:
                if type == "save":
                    blog = Blog.objects.create(title=title, abstract=abstract, status='2', user=request.my_user,
                                               is_show=False)
                else:
                    blog = Blog.objects.create(title=title, abstract=abstract, user=request.my_user)

                Content.objects.create(content=content, blog=blog)

                for item in category:
                    try:
                        old_cate = Category.objects.get(category=item)
                    except:
                        # 未查询到分类，则创建新分类
                        new_cate = blog.category_set.create(category=item)
                    else:
                        # 查询到分类,添加多对多属性
                        old_cate.blog.add(blog)
                # 添加历史记录
                try:
                    request.my_user.userhistory
                except:
                    # 创建博客记录
                    UserHistory.objects.create(user=request.my_user)
                UserHistory.objects.filter(user=request.my_user).update(original=F('original') + 1)
            except:
                return error(500, '保存失败')
        r9.lpush('featured_ids', blog.id)
        return success({'blog_id': blog.id})


class Details(View):
    def dispatch(self, request, *args, **kwargs):
        try:
            blog = Blog.objects.get(id=kwargs['blog_id'], is_show=True, status=1)
            request.blog = blog
        except:
            return error(404, "博客不存在")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, blog_id, type):
        # 获取博客信息或者评论
        if type == 'user_info':
            res = self.get_user_info(request, blog_id)
        elif type == 'content':
            res = self.get_content(request, blog_id)
        elif type == 'comment':
            res = self.get_comment(request, blog_id)
        elif type == 'user_detail':
            res = self.get_user_detail(request, blog_id)
        elif type == 'blog_list':
            res = self.get_blog_list(request, blog_id)
        else:
            res = ''
        if res:
            return success(res)
        return error(400, '意外的错误')

    @logging_check
    def patch(self, request, blog_id, type):
        """
            点赞
        """
        try:
            if type == 'praise':
                blog = request.blog
                user = request.my_user
                master = User.objects.get(blog=blog)
                if BrowserHistory.objects.filter(blog=blog, user=user, praise=False).update(praise=True):
                    # 更新点赞数
                    UserHistory.objects.filter(user=master).update(praise=F('praise') + 1)
                    update.update_praise(blog_id)
                    return success()
                elif BrowserHistory.objects.filter(blog=blog, user=user, praise=True).update(praise=False):
                    UserHistory.objects.filter(user=master).update(praise=F('praise') - 1)
                    update.update_praise(blog_id, -1)
                    return success(code=201)
        except:
            pass
        return error(400, '意外的错误')

    def patch_praise(self,request,blog_id):
        pass

    @logging_check
    def post(self, request, blog_id, type):
        """
            评论
        """
        try:
            obj = json.loads(request.body)
            blog = request.blog
            user = request.my_user
            type = obj['type']
            comment_info = obj['comment_info']
            to_user_id = obj.get('to_user_id')
            parent_comment_id = obj.get('parent_comment_id')
        except:
            return error(400, '缺少必要参数')
        if not comment_info:
            return error(400, '请输入评论内容')
        with transaction.atomic():
            try:
                # 子评论
                if to_user_id and parent_comment_id:
                    # 父级评论存在
                    Comment.objects.get(id=parent_comment_id)
                    # 检查目标用户
                    User.objects.get(id=to_user_id)
                    comment = Comment.objects.create(genre=type, parent_comment_id=parent_comment_id,
                                                     to_user_id=to_user_id,
                                                     blog=blog, user=user)
                    comment_history = self.set_comment_history(type, comment, comment_info)
                    res = {
                        'parent_comment_id': comment.parent_comment_id,
                        'type': comment.genre,
                        'create_time': str(comment.create_time).split('.')[0],
                        'user_id': comment.user.id,
                        'avatar': str(comment.user.avatar),
                        'user_name': comment.user.username,
                        'to_user_id': comment.to_user_id,
                        'to_user_name': User.objects.filter(id=comment.to_user_id)[0].username
                    }
                else:
                    comment = Comment.objects.create(genre=type, blog=blog, user=user)
                    comment_history = self.set_comment_history(type, comment, comment_info)
                    res = {
                        'comment_id': comment.id,
                        'type': comment.genre,
                        'create_time': str(comment.create_time).split('.')[0],
                        'user_id': comment.user.id,
                        'avatar': str(comment.user.avatar),
                        'user_name': comment.user.username,
                    }
                master = User.objects.get(blog=blog)
                UserHistory.objects.filter(user=master).update(comments=F('comments') + 1)
                update.update_comment(blog_id)
            except:
                return error(422, '评论失败')
        return success(res)

    def get_comment_history(self, request, comment):
        if comment.genre == 'text':
            content = comment.commenthistory.text
        elif comment.genre == 'img':
            content = comment.commenthistory.img
        elif comment.genre == 'link':
            content = comment.commenthistory.link
        else:
            raise
        return content

    def set_comment_history(self, genre, comment, info):
        if genre == 'text':
            c = CommentHistory.objects.create(text=info, comment=comment)
        elif genre == 'img':
            c = CommentHistory.objects.create(img=info, comment=comment)
        elif genre == 'link':
            c = CommentHistory.objects.create(link=info, comment=comment)
        else:
            raise
        return c

    def get_user_info(self, request, blog_id):
        # TODO 要做一个redis缓存
        try:
            res = {}
            user = Blog.objects.get(id=blog_id).user

            try:
                user_history = UserHistory.objects.get(user=user)
            except:
                user_history = UserHistory.objects.create(user=user)
            res['username'] = user.username
            res['avatar'] = str(user.avatar)
            res['original'] = user_history.original
            res['browse'] = user_history.browse
            res['id'] = user.id
            # TODO 应查找所有用户发表博客总分 进行排序
            # 这里使用博客原创数量
            rank_list = list(User.objects.all().extra(tables=['user_user', 'user_userhistory'],
                                                      where=['user_user.id=user_userhistory.user_id'],
                                                      order_by=['-user_userhistory.original',
                                                                'user_user.id']).values_list('id', flat=True)[
                             : 100])
            print(rank_list)
            res['rank'] = rank_list.index(res['id']) + 1
            res['newblog'] = list(
                Blog.objects.filter(user=user).order_by('-create_time').values_list('id', 'title')[:5])
        except:
            return
        return res

    def get_content(self, request, blog_id):
        blog = request.blog
        praise_type = False
        if user_check(request):
            praise_type = True
            # 更新
            if not BrowserHistory.objects.filter(blog=blog, user=request.user).update(
                    update_time=datetime.datetime.now()):
                # 更新失败  --> 创建浏览记录
                BrowserHistory.objects.create(blog=blog, user=request.user)
                praise_type = False
            if praise_type:
                praise_type = BrowserHistory.objects.get(blog=blog, user=request.user).praise
        user = User.objects.get(blog=blog)
        # 博主总浏览加一
        UserHistory.objects.filter(user=user).update(browse=F('browse') + 1)
        # 博客浏览加一
        update.update_browse(blog_id)
        # 获取基础信息
        blog_info = update.get_blog_info(blog_id)[0]
        # 获取内容
        content = blog.content.content
        res = {'title': blog_info['title'],
               'original': int(blog_info['original']),
               'content': content,
               'create_time': blog_info['create_time'],
               'comment': blog_info['comment'],
               'favorite': blog_info['favorite'],
               'praise': blog_info['praise'],
               'browse': blog_info['browse'],
               'praise_type': praise_type,
               }
        return res

    def get_comment(self, request, blog_id):
        try:
            comment_list = []
            # 这个博客下的所有评论
            parent_comment_list = Comment.objects.filter(blog_id=blog_id, is_active=True).order_by('create_time')
            for comment in parent_comment_list:
                # 评论类型
                info = self.get_comment_history(request, comment)
                parent_comment_id = comment.parent_comment_id
                # 子评论
                if parent_comment_id:
                    # 查询对应一级评论
                    for item in comment_list:
                        if item['comment_id'] == parent_comment_id:
                            # 添加到子评论列表
                            item['child_comment'].append({
                                'avatar': str(comment.user.avatar),
                                'comment_id': comment.id,
                                'type': comment.genre,
                                'info': info,
                                'create_time': str(comment.create_time).split('.')[0],
                                'user_id': comment.user.id,
                                'user_name': comment.user.username,
                                'to_user_id': comment.to_user_id,
                                'to_user_name': User.objects.filter(id=comment.to_user_id)[0].username
                            })
                            break
                else:
                    # 一级评论
                    comment_list.append({
                        'comment_id': comment.id,
                        'type': comment.genre,
                        'info': info,
                        'create_time': str(comment.create_time).split('.')[0],
                        'user_id': comment.user.id,
                        'avatar': str(comment.user.avatar),
                        'user_name': comment.user.username,
                        'child_comment': []
                    })
            res = {'comment_list': comment_list}
            return res
        except:
            return

    def get_user_detail(self, request, blog_id):
        try:
            res = {}
            user = User.objects.get(id=blog_id)
            print(user)
            try:
                user_history = UserHistory.objects.get(user=user)
            except:
                user_history = UserHistory.objects.create(user=user)
            res['username'] = user.username
            res['avatar'] = str(user.avatar)
            res['original'] = user_history.original
            res['browse'] = user_history.browse
            res['id'] = user.id
            # TODO 应查找所有用户发表博客总分 进行排序
            # 这里使用博客原创数量
            rank_list = list(User.objects.all().extra(tables=['user_user', 'user_userhistory'],
                                                      where=['user_user.id=user_userhistory.user_id'],
                                                      order_by=['-user_userhistory.original',
                                                                'user_user.id']).values_list('id', flat=True)[: 100])
            res['rank'] = rank_list.index(res['id']) + 1
            res['all_blog'] = len(user.blog_set.filter(is_show=True, status=1).annotate(num=Count('id')))
            res['comments'] = user_history.comments
            res['praise'] = user_history.praise
            return res
        except:
            return False

    def get_blog_list(self, request, user_id):
        try:
            blog_ids = list(Blog.objects.filter(user_id=user_id).extra(tables=['user_user', 'blog_blog'],
                                                                       where=['user_user.id=blog_blog.user_id'],
                                                                       order_by=[
                                                                           '-blog_blog.create_time', ]).values_list(
                'id', flat=True))
            res = update.get_blog_info(blog_ids)
            return res
        except:
            return False
