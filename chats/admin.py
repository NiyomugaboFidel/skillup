from django.contrib import admin
from .models import Thread, DirectMessage

admin.site.register(Thread)
admin.site.register(DirectMessage)