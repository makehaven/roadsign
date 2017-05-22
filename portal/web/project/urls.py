"""URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
from django.contrib import admin
import django.contrib.auth.views

from roadsign import urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # Uncomment for oauth support
    #url(r'^oauth/', include("oauth.urls")),

    # Auth urls
    url(r'^accounts/login$', django.contrib.auth.views.login,
        {'template_name': 'login.html'},
        name="login"),
    url(r'^accounts/logout$', django.contrib.auth.views.logout,
        {'template_name': 'logout.html'},
        name="logout"),
    url(r'^accounts/change_password$',
        django.contrib.auth.views.password_change,
        {'template_name': 'password_change.html',
         'post_change_redirect':
             'django.contrib.auth.views.password_change_done'},
        name="change_password"),
    url(r'^accounts/change_password_done$',
        django.contrib.auth.views.password_change_done,
        {'template_name': 'password_change_done.html'}),

    url(r'', include(urls)),
]
