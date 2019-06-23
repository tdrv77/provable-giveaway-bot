from django.contrib import admin
from django.contrib.auth.models import User, Group

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.site_header = 'Discord Bot'
admin.site.site_title = admin.site.site_header
