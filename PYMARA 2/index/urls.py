from django.urls import path
from . import views

urlpatterns = [

    # http://127.0.0.1:8000/v1/index/judge_login
    path("judge_login", views.JudgeLoginView.as_view()),

    # http://127.0.0.1:8000/v1/index/show_blogs
    path("show_blogs", views.ShowBlogsView.as_view()),

]
