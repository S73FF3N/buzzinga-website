from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from gameFiles import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    path('account/', include(('account.urls', 'account'), namespace='account')),
    path('gameFiles/', include(('gameFiles.urls', 'gameFiles'), namespace='gamefiles')),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static('uploads', document_root=settings.UPLOAD_ROOT)
