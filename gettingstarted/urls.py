from django.conf.urls import include, url
from django.urls import path

from django.contrib import admin
admin.autodiscover()

import psykahut.views

urlpatterns = [
    url(r'^$', psykahut.views.index, name='index'),
    url(r'^register/$', psykahut.views.register, name='index'),
    url(r'^open_question/$', psykahut.views.open_question, name='index'),
    path('admin/', admin.site.urls),
]
