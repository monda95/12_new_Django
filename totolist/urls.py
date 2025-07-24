from django.contrib import admin
from django.urls import path
from todo import views

def index(request):
    return HttpResponse('Hello')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("todo/", views.todo_list),
    path('todo/<int:pk>/', views.todo_detail, name='todo_detail'),
    path('', index),
]