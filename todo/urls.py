from django.urls import path
from . import cb_views

app_name = 'todo'

urlpatterns = [
    path("", cb_views.TodoListView.as_view(), name="list"),
    path("<int:todo_pk>/", cb_views.TodoDetailView.as_view(), name="detail"),
    path('create/', cb_views.TodoCreateView.as_view(), name='create'),
    path("<int:todo_pk>/update/", cb_views.TodoUpdateView.as_view(), name="update"),
    path("<int:todo_pk>/delete/", cb_views.TodoDeleteView.as_view(), name="delete"),
    path('comment/create/<int:todo_pk>/', cb_views.CommentCreateView.as_view(), name='comment_create'),
    path('comment/delete/<int:comment_pk>/', cb_views.CommentDeleteView.as_view(), name='comment_delete'),
]