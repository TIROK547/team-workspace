from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_note, name='create_note'),
    path('', views.get_notes, name='get_notes'),
    path('<int:note_id>/delete/', views.delete_note, name='delete_note'),
    path('stream/', views.sse_stream, name='notes_sse_stream'),
]