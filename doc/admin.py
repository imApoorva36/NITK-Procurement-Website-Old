from django.contrib import admin
from .models import UserData

# Register your models here.
# @admin.register(UserData)
# class UserDataModel(admin.ModelAdmin):
#     productlist_display = ('name', 'students', 'company')

admin.site.register(UserData)