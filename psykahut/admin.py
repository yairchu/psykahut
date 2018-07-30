from django.contrib import admin

from .models import *

admin.site.register(Topic)
admin.site.register(Question)
admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Answer)
admin.site.register(Vote)
