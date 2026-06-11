from django.contrib import admin
from .models import Application, Job, Profile, Review, Payment, Message, Notification, JobImage

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

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'trade', 'county', 'hourly_rate', 'is_available')
    list_filter = ('role', 'county', 'is_available')
    search_fields = ('user__username', 'trade', 'county')

admin.site.register(Review)
admin.site.register(Payment)
admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(JobImage)