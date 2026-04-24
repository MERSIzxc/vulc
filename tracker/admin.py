from django.contrib import admin
from .models import UserProfile, Grade

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'vulcan_email', 'last_sync']
    search_fields = ['user__username', 'vulcan_email']

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'value', 'weight', 'date', 'teacher']
    list_filter = ['subject', 'user']
    search_fields = ['user__username', 'subject', 'description']
