from django.contrib.auth.models import User
from django.db import models


class Note(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    text_content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
