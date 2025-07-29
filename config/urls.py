from django.contrib import admin
from django.urls import path, include
from member import views as member_views
from todo import views as todo_views

urlpatterns = [
    path('', member_views.index, name='index'),
    path('admin/', admin.site.urls),
    path('todo/', include('todo.urls')),

    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', member_views.sign_up, name='signup'),
    path('login/', member_views.login, name='login'),
]