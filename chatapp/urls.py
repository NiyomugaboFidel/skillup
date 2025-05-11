from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from posts.views import HomeView
from courses.views import HomePageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePageView.as_view(), name='index'),
    path('comunity/', HomeView.as_view(), name='home'),
    path('', include('courses.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('quiz.urls')),
    path('posts/', include('posts.urls')),
    path('messages/', include('chats.urls')),
    path('notifications/', include('notifications.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('quiz/', include('quiz.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
