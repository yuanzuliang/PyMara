import json

from django.db.models import Count
from django.http import JsonResponse
from django.views import View

from Public.publictoken import logging_check, user_check
from Public.tools import success, error
from Public.update_blog_history import UpdateBlogHistory
from blog.models import *
from user.models import UserInfo

update = UpdateBlogHistory()


class BlogInfo(View):
    @logging_check
    def get(self, request, user_id):
        """
            获取博客
        """
        # 获取所有博客ID
        blog_ids = Blog.objects.filter(user=request.my_user).values_list('id', flat=True)
        # 获取所有博客信息
        blog_list = update.get_blog_info(list(blog_ids))
        return success(blog_list)

    @logging_check
    def patch(self, request, user_id):
        """
            删除博客
        """
        blog_id = json.loads(request.body).get('blog_id')
        if update.update_status(blog_id, '3'):
            return success()
        return error(404, '删除失败')


class Details(View):
    def get(self,request, user_id, type):
        if type == 'user_detail':
            res = self.get_user_detail(request,user_id)
        elif type=='user_info':
            res=self.get_user_info(request,user_id)
        else:
            res=''
        if res:
            return success(res)
        return error(400, '加载失败')

    @logging_check
    def post(self, request,user_id,type):
        # 用户修改个人信息
        json_obj = json.loads(request.body.decode())
        nickname = json_obj["nickname"]
        name = json_obj["name"]
        gender = json_obj["gender"]
        age = json_obj["age"]
        dict_sex = {"男": "1", "女": "2", "保密": "3"}
        old_user = request.my_user
        # 先找一下有没有对应数据
        try:
            user_info = UserInfo.objects.get(user=old_user)
        except:
            # 用户信息 UserInfo 已经创建
            user_info = UserInfo.objects.create(name=name, age=age, sex=dict_sex[gender], user=old_user)
        else:
            user_info.name = name
            user_info.age = age
            user_info.sex = dict_sex[gender]
            user_info.save()
        finally:
            try:
                nick_user = User.objects.get(id=old_user.id)
                nick_user.username = nickname
                nick_user.save()
            except:
                return JsonResponse({"code": 701, "data": "昵称修改失败"})

        dict_data = {}
        dic_sex = {"1": "男", "2": "女", "3": "保密"}
        dict_data["nickname"] = nick_user.username
        dict_data["name"] = user_info.name
        dict_data["gender"] = dic_sex[user_info.sex]
        dict_data["age"] = user_info.age
        return success(dict_data)
    def get_user_detail(self, request,user_id):
        try:
            res = {}
            user = User.objects.get(id=user_id)
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
    def get_user_info(self, request, user_id):
        if user_check(request):
            # 个人信息页获取数据用于页面显示
            old_user = request.user

            nickname = old_user.username

            try:
                user_info = UserInfo.objects.get(user=old_user)
            except:
                return {"nickname": nickname}

            dict_data = {}
            dic_sex = {"1": "男", "2": "女", "3": "保密"}
            dict_data["nickname"] = nickname
            dict_data["name"] = user_info.name
            dict_data["gender"] = dic_sex[user_info.sex]
            dict_data["age"] = user_info.age
            return dict_data
        return