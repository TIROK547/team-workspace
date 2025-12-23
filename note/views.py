import asyncio
import json

import redis.asyncio as aioredis
from django.http import StreamingHttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Note

@login_required
def create_note(request):
    if request.method == 'POST':
        user = request.user
        text_content = request.POST.get("text_content")

        if not text_content or len(text_content) < 5:
            return JsonResponse({'message': 'message should be at least a 5char long str'}, status=400)

        try:
            Note.objects.create(
                user=user,
                text_content=text_content
            )
            return JsonResponse({'message':'note created'},status=200)
        except Exception as e:
            return JsonResponse({'message': f'Failed to create note: {str(e)}'}, status=500)
    return JsonResponse({'message':'wrong method used, use POST'},status=405)

@login_required
async def sse_stream(request):
    async def event_stream():
        redis = None
        pubsub = None
        try:
            redis = await aioredis.from_url("redis://localhost:6379")
            pubsub = redis.pubsub()
            await pubsub.subscribe("note_updates")

            yield 'event: connected\ndata: {"status": "connected"}\n\n'

            try:
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        data = message["data"].decode("utf-8")
                        yield f"event: update\ndata: {data}\n\n"
            except asyncio.CancelledError:
                raise
        except Exception as e:
            yield f'event: error\ndata: {{"error": "Failed to connect to Redis: {str(e)}"}}\n\n'
        finally:
            if pubsub:
                await pubsub.unsubscribe("note_updates")
            if redis:
                await redis.close()

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
