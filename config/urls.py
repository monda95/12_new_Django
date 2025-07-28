from django.contrib import admin
from django.urls import path, include
from member import views as member_views
from todo import views as todo_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('todo/', todo_views.todo_list, name='todo_list'),
    path('todo/create/', todo_views.todo_create, name='todo_create'),
    path('todo/<int:pk>/', todo_views.todo_detail, name='todo_detail'),
    path('todo/<int:pk>/update/', todo_views.todo_update, name='todo_update'),
    path('todo/<int:pk>/delete/', todo_views.todo_delete, name='todo_delete'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', member_views.sign_up, name='signup'),
    path('', member_views.index, name='index'),
]