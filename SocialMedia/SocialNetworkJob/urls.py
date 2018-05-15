from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import include,url
from django.conf.urls.static import settings, static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reseausocial/', include("SocialMedia.urls")),
    path('main/', include("main_app.urls")),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
