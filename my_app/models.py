from django.db import models
from django.conf import settings



class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Client(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name  
      
class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey('Client', on_delete=models.CASCADE, default=1)
    slug = models.SlugField(null=True, blank=True)


    def __str__(self):
        return self.title
    
class Message(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.job.title} | {self.sender} → {self.receiver}: {self.content[:30]}"
    

class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='my_applications')
    applied_at = models.DateTimeField(auto_now_add=True)


