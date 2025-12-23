from django.urls import path

from .views import sse_stream, create_note

urlpatterns = [
    path("events/", sse_stream, name="sse_stream"),
    path("notes/new/", create_note, name="create_new_note")
]
