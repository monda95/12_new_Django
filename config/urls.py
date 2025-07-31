from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from member import views as member_views
from todo import views as todo_views
from django.conf.urls.static import static

urlpatterns = [
    path('', member_views.index, name='index'),
    path('admin/', admin.site.urls),
    path('todo/', include('todo.urls')),

    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', member_views.sign_up, name='signup'),
    path('login/', member_views.login, name='login'),
    #summetnote
    path('summernote/', include('django_summernote.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)