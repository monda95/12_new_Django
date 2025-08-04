from django.urls import path
from . import views

app_name = 'member'

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('signup/done/', views.SignupDoneView.as_view(), name='signup_done'),
    path('verify/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('', views.IndexView.as_view(), name='index'), # 루트 경로를 IndexView로 연결
]
