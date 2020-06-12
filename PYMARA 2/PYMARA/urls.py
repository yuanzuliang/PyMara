"""PYMARA URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # http://127.0.0.1:8000/v1/logreg/...
    path("v1/logreg/", include("logreg.urls")),

    # http://127.0.0.1:8000/v1/index/...
    path("v1/index/", include("index.urls")),

    path("v1/blog/", include("blog.urls")),

    path("v1/user/", include("user.urls")),

    # http://127.0.0.1:8000/v1/user/...
    # path("v1/user/", include("person.urls")),

]

urlpatterns += static(settings.MY_MEDIA_URL, document_root=settings.MY_MEDIA_ROOT)
urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
