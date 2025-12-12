from django.contrib import admin
from apps.main.models import *

# Register your models here.

class AdminCategory(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')

class AdminSetting(admin.ModelAdmin):
    list_display = ('id', 'category', 'key', 'alias', 'mode', 'value', 'file')


admin.site.register(Category, AdminCategory)
admin.site.register(Setting, AdminSetting)