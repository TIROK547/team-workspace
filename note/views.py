# views.py
import asyncio
import json
import redis.asyncio as aioredis
from django.http import StreamingHttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Note
from projects.models import Project

@login_required
@require_http_methods(["POST"])
def create_note(request):
    user = request.user
    text_content = request.POST.get("text_content", "").strip()
    project_id = request.POST.get("project_id")
    project = Project.objects.get(id=project_id)
    if not text_content or len(text_content) < 5:
        return JsonResponse({'message': 'پیام باید حداقل ۵ کاراکتر باشد'}, status=400)

    try:
        note = Note.objects.create(
            user=user,
            text_content=text_content,
            project=project if project else None
        )
        return JsonResponse({
            'message': 'نوت ایجاد شد',
            'note': {
                'id': note.id,
                'text': note.text_content,
                'date': note.created_at.strftime('%Y/%m/%d'),
                'time': note.created_at.strftime('%H:%M'),
            }
        }, status=201)
    except Exception as e:
        return JsonResponse({'message': f'خطا در ایجاد نوت: {str(e)}'}, status=500)


@login_required
def get_notes(request):
    """Get existing notes for a project"""
    project_id = request.GET.get('project_id')
    project = Project.objects.get(id=project_id)
    notes = Note.objects.filter(project=project).select_related('user')[:20]

    notes_data = [{
        'id': note.id,
        'user': note.user.username,
        'text': note.text_content,
        'date': note.created_at.strftime('%Y/%m/%d'),
        'time': note.created_at.strftime('%H:%M'),
    } for note in notes]

    return JsonResponse({'notes': notes_data})


@login_required
@require_http_methods(["DELETE"])
def delete_note(request, note_id):
    """Delete a note"""
    try:
        note = Note.objects.get(id=note_id)
        note.delete()
        return JsonResponse({'message': 'نوت حذف شد'}, status=200)
    except Note.DoesNotExist:
        return JsonResponse({'message': 'نوت یافت نشد'}, status=404)


@login_required
async def sse_stream(request):
    project_id = request.GET.get('project_id')

    async def event_stream():
        redis = None
        pubsub = None
        try:
            redis = await aioredis.from_url("redis://localhost:6379")
            pubsub = redis.pubsub()
            await pubsub.subscribe("note_updates")

            yield 'event: connected\ndata: {"status": "connected"}\n\n'

            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"].decode("utf-8"))
                    # Filter by project if specified
                    if project_id and str(data.get('project_id')) != str(project_id):
                        continue
                    yield f"event: note\ndata: {json.dumps(data)}\n\n"

        except asyncio.CancelledError:
            pass
        except Exception as e:
            yield f'event: error\ndata: {{"error": "{str(e)}"}}\n\n'
        finally:
            if pubsub:
                await pubsub.unsubscribe("note_updates")
            if redis:
                await redis.close()

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response