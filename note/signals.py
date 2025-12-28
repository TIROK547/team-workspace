import json
import redis
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Note

redis_client = redis.Redis(host="localhost", port=6379, db=0)

@receiver(post_save, sender=Note)
def notify_on_create_note(sender, instance, created, **kwargs):
    if created:
        note_data = {
            'id': instance.id,
            'user': instance.user.username,
            'text': instance.text_content,
            'project_id': instance.project.id,
            'date': instance.created_at.strftime('%Y/%m/%d'),
            'time': instance.created_at.strftime('%H:%M'),
        }
        redis_client.publish("note_updates", json.dumps(note_data))
