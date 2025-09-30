from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from gallery import views
from gallery.views import AdminLoginView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", AdminLoginView.as_view(), name="admin_login"),
    path("logout/", views.admin_logout, name="logout"),
    path("", views.home, name="home"),
    path("gallery/", views.gallery, name="gallery"),
    path("thanksgiving/", views.thanksgiving_gallery, name="thanksgiving"),
    path("upload/", views.upload_image, name="upload_image"),
    path("announcements/", views.announcements, name="announcements"),
    path("announcements/add/", views.add_announcement, name="add_announcement"),
    path("delete/<int:image_id>/", views.delete_image, name="delete_image"),
    path("brief-history/", views.brief_history, name="brief_history"),
    path("our-team/", views.our_team, name="our_team"),
    path("parish-pastoral-council/", views.parish_pastoral_council, name="parish_pastoral_council"),
    path("parish-laity-council/", views.parish_laity_council, name="parish_laity_council"),

    path("harvest-events/", views.harvest_events, name="harvest_events"),
    path("harvest-events/add/", views.add_harvest_event, name="add_harvest_event"),
    path("harvest-events/delete/<int:event_id>/", views.delete_harvest_event, name="delete_harvest_event"),


    path("bulletins/", views.bulletin_list, name="bulletin_list"),
    path("bulletins/add/", views.bulletin_add, name="bulletin_add"),
    path("bulletins/<int:pk>/", views.bulletin_detail, name="bulletin_detail"),
    path("bulletins/<int:pk>/update_readings/", views.bulletin_update_readings, name="bulletin_update_readings"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

