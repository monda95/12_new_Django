from django.urls import path
from . import views

app_name = 'todo'

urlpatterns = [
    path("", views.todo_list, name="todo_list"),
    path("<int:pk>/", views.todo_detail, name="todo_detail"),
]