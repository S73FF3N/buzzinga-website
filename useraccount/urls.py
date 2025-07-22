from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

app_name = 'useraccount'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('profile/<str:per_page>/', views.profile_view, name='profile'),
    path('download/<str:active_table>/<str:element_string>/', views.DownloadView.as_view(), name='download'),
    path('download/<str:active_table>/all/', views.DownloadView.as_view(), name='download_all'),
]