from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vulcan_email = models.EmailField(blank=True)
    vulcan_password = models.CharField(max_length=255, blank=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    api_key = models.CharField(max_length=64, unique=True, null=True, blank=True)

    def __str__(self):
        return self.user.username

class Grade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    value = models.CharField(max_length=10)
    weight = models.IntegerField()
    description = models.TextField()
    date = models.DateTimeField(null=True, blank=True)
    teacher = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.subject} - {self.value}"
