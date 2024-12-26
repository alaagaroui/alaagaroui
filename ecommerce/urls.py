from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from store.views import AdminLogoutView

urlpatterns = [
    path('admin/logout/', AdminLogoutView.as_view(), name='admin_logout'),
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
