from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from gallery import views
from gallery.views import AdminLoginView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", AdminLoginView.as_view(), name="admin_login"),  # use class-based login
    path("logout/", views.admin_logout, name="logout"),  # custom logout
    path("", views.home, name="home"),
    path("gallery/", views.gallery, name="gallery"),
    path("thanksgiving/", views.thanksgiving_gallery, name="thanksgiving"),
    path("upload/", views.upload_image, name="upload_image"),  # single upload path
    path("announcements/", views.announcements, name="announcements"),
    path("announcements/add/", views.add_announcement, name="add_announcement"),
    path("delete/<int:image_id>/", views.delete_image, name="delete_image"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
