from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from notifications.views_pwa import save_push_subscription, pwa_manifest
from projects.views_home import home_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('calendar/', include('calendar_app.urls')),
    path('projects/', include('projects.urls')),
    path('tasks/', include('tasks.urls')),
    path('chat/', include('chat.urls')),
    path('attachments/', include('attachments.urls')),
    path('notifications/', include('notifications.urls')),
    path('api/push-subscription/', save_push_subscription, name='push_subscription'),
    path('manifest.json', pwa_manifest, name='pwa_manifest'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('notes/',include('note.urls')),
    path('', home_redirect, name='home'),
]

# اضافه کردن مسیر media
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
