from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('profile/<str:per_page>/', views.profile_view, name='profile'),
    path('download/<str:active_table>/', views.download_all_elements, name='download'),
    path('download/<str:active_table>/<str:element_string>', views.download_elements, name='download'),
]