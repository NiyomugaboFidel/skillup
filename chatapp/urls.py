from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from posts.views import HomeView
from courses.views import IndexView


urlpatterns = [
    path('admin/', admin.site.urls),
  path('', IndexView.as_view(), name='index'),

    path('/comunity', HomeView.as_view(), name='home'),
    path('courses/', include('courses.urls')),
    path('accounts/', include('accounts.urls')),
    path('posts/', include('posts.urls')),
    path('messages/', include('chats.urls')),
    path('notifications/', include('notifications.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
