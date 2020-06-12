from django.views import View
from django.http import JsonResponse
from Public.publictoken import logging_check

class JudgeLoginView(View):

    @logging_check
    def post(self, request):
        user = request.my_user

        return JsonResponse({"code":200, "data": "", "uname": user.username})


class ShowBlogsView(View):

    def get(self, request):
        """
        list_blogs = [
            {
                "userid": xx,
                "username": "",
                "title": "",
                "link": "",
                "like": xx,
                "read": xx,
                "comment": xx,

            },
            {...},
            {...},
        ]
        """

        return JsonResponse({"code":200, "data": "连接成功"})



