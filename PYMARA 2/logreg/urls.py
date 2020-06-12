from django.urls import path
from . import views

urlpatterns = [
    # http://127.0.0.1:8000/v1/logreg/judge_phone_number
    path("judge_phone_number", views.JudgePhoneNumber.as_view()),

    # http://127.0.0.1:8000/v1/logreg/register
    path("register", views.Register.as_view()),

    # http://127.0.0.1:8000/v1/logreg/send_message
    path("send_message", views.SendMessage.as_view()),

    # http://127.0.0.1:8000/v1/logreg/login
    path("login", views.UserLogin.as_view()),

    # http://127.0.0.1:8000/v1/logreg/find_psd
    path("find_psd", views.FindPsd.as_view()),

    # http://127.0.0.1:8000/v1/logreg/change_psd
    path("change_psd", views.ChangePsd.as_view()),

    # http://127.0.0.1:8000/v1/logreg/judge_old_phone
    path("judge_old_phone", views.JudgeOldPhone.as_view()),

    # http://127.0.0.1:8000/v1/logreg/weibo/login
    path("weibo/login", views.WeiboLoginView.as_view()),

    # http://127.0.0.1:8000/v1/logreg/weibo/user?code=xxx (get)
    path("weibo/user", views.WeiboUserView.as_view()),

    # http://127.0.0.1:8000/v1/logreg/weibo/user/<str:wuid>
    path("weibo/user/<str:wuid>", views.BindPymaraUser.as_view()),
]


