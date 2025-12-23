import asyncio
import json

import redis.asyncio as aioredis
from django.http import StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from .models import Note

@login_required
def create_note(request):
    if request.method == 'POST':
        Note.objects.create(
            user=request.user,
            text_content=request.POST.get("text_content")
        )
        return {'message':'note created','status':200}

async def sse_stream(request):
    async def event_stream():
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
            await pubsub.unsubscribe("note_updates")
            await redis.close()
            raise

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
