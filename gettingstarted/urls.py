from django.conf.urls import include, url
from django.urls import path

from django.contrib import admin
admin.autodiscover()

import psykahut.views

urlpatterns = [
    url(r'^$', psykahut.views.index),
    url(r'^manage/$', psykahut.views.manage),
    url(r'^manage/start_new/$', psykahut.views.start_new),
    url(r'^register/$', psykahut.views.register),
    url(r'^open_question/$', psykahut.views.open_question),
    url(r'^quiz/$', psykahut.views.answer_quiz),
    path('summary/<int:question_id>/', psykahut.views.summary),
    path('admin/', admin.site.urls),
]
