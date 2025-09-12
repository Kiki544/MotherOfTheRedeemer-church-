from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from .models import GalleryImage, Announcement, AdminSecretCode
from .forms import AnnouncementForm, AdminLoginForm, GalleryUploadForm

# Home page
def home(request):
    return render(request, "home.html")

# General gallery
def gallery(request):
    category = request.GET.get("category", "general")
    images = GalleryImage.objects.filter(category=category).order_by("-uploaded_at")
    return render(request, "gallery.html", {"images": images, "selected_category": category})

# Thanksgiving gallery
def thanksgiving_gallery(request):
    images = GalleryImage.objects.filter(category="thanksgiving").order_by("-uploaded_at")
    return render(request, "thanksgiving.html", {"images": images})

# Upload image
@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def upload_image(request):
    if request.method == "POST":
        form = GalleryUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("gallery")
    else:
        form = GalleryUploadForm()
    return render(request, "upload_image.html", {"form": form})

from django.shortcuts import get_object_or_404

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def delete_image(request, image_id):
    image = get_object_or_404(GalleryImage, id=image_id)
    if request.method == "POST":
        image.delete()
        return redirect("gallery")  # send back to gallery after delete
    return render(request, "confirm_delete.html", {"image": image})

# Announcements
def announcements(request):
    notes = Announcement.objects.order_by("-date_posted")
    return render(request, "announcements.html", {"notes": notes})

from django.shortcuts import render

def brief_history(request):
    return render(request, 'brief_history.html')

def our_team(request):
    return render(request, 'our_team.html')

def parish_pastoral_council(request):
    return render(request, 'parish_pastoral_council.html')

def parish_laity_council(request):
    return render(request, 'parish_laity_council.html')


# Add announcement
@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def add_announcement(request):
    if request.method == "POST":
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("announcements")
    else:
        form = AnnouncementForm()
    return render(request, "add_announcement.html", {"form": form})

# Admin logout
@login_required
def admin_logout(request):
    logout(request)
    return redirect("home")

# Class-based login view for admin
class AdminLoginView(LoginView):
    authentication_form = AdminLoginForm
    template_name = "admin_login.html"

    def form_valid(self, form):
        # Extra check for special code
        code = form.cleaned_data.get("special_code")
        if not AdminSecretCode.objects.filter(code=code).exists():
            form.add_error("special_code", "Invalid special code")
            return self.form_invalid(form)
        return super().form_valid(form)
