import json

import redis
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Note

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@receiver(post_save, sender=Note)
def notify_on_create_note(sender, instance, created, **kwargs):
        if created:
        message = {
            'type': 'created',
            'id': instance.id,
            'data': {
                'field1': instance.field1,
                'field2': instance.field2,
            }
        }
        redis_client.publish('yourmodel_updates', json.dumps(message))
