from django.urls import path, re_path

from blog import views

urlpatterns = [

    # 搜索
    # http://127.0.0.1:8000/v1/blog/search/
    path('search/', views.Search.as_view()),
    # 排行 -->修改
    # http://127.0.0.1:8000/v1/blog/rank/
    path('rank/<str:type>/<int:page>', views.Rank.as_view()),

    # 编辑  -->修改
    # http://127.0.0.1:8000/v1/blog/editor/
    path('editor/', views.Editor.as_view()),

    # 图片上传  -->修改
    # http://127.0.0.1:8000/v1/blog/image/
    # path('img/', views.Image.as_view()),
    # 必须使用正则匹配
    re_path(r'^img/$', views.Image.as_view()),

    # 博客显示
    # http://127.0.0.1:8000/v1/blog/details/<blog_id>/<请求类型info/comment>
    path('details/<int:blog_id>/<str:type>', views.Details.as_view()),


]
