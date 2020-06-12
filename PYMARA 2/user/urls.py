from django.urls import path

from user import views

urlpatterns = [
    path('<str:user_id>/blog_info/', views.BlogInfo.as_view()),
    path('details/<str:user_id>/<str:type>', views.Details.as_view()),
]
