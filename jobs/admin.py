from django.contrib import admin
from .models import Application
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'client', 'category', 'remote', 'created_at')
    list_filter = ('category', 'remote', 'client')
    search_fields = ('title', 'description', 'client__username')
    list_display_links = ('id', 'title')
    ordering = ('-created_at',)

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'freelancer', 'applied_at')
    search_fields = ('job__title', 'freelancer__username')    
