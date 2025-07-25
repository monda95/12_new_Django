from django.contrib import admin
from django.urls import path, include
from member import views as member_views
from todo import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("todo/", include("todo.urls")),
    path('accounts/', include("django.contrib.auth.urls")),
    path('signup/', member_views.sign_up, name='signup'),
    path('login/', member_views.login, name='login'),
    path("", include("todo.urls")),


    ]