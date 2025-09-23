from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from .models import GalleryImage, Announcement, AdminSecretCode, Bulletin

# Home page
def home(request):
    return render(request, "home.html")


# General gallery
def gallery(request):
    category = request.GET.get("category", "general")  # default to general
    images = GalleryImage.objects.filter(category=category).order_by("-uploaded_at")
    return render(request, "gallery.html", {"images": images, "selected_category": category})


# Thanksgiving gallery
def thanksgiving_gallery(request):
    images = GalleryImage.objects.filter(category="thanksgiving").order_by("-uploaded_at")
    return render(request, "thanksgiving.html", {"images": images})


# Upload image (with optional caption and category)
@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def upload_image(request):
    if request.method == "POST":
        form = GalleryUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # saves image, caption, and category
            return redirect("gallery")  # redirect to gallery after upload
    else:
        form = GalleryUploadForm()
    return render(request, "upload_image.html", {"form": form})


# Display announcements
def announcements(request):
    notes = Announcement.objects.order_by("-date_posted")
    return render(request, "announcements.html", {"notes": notes})


# Add announcement (admin only)
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


# Admin login with special code
def admin_login(request):
    if request.method == "POST":
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("home")  # redirect to home page
    else:
        form = AdminLoginForm()
    return render(request, "admin_login.html", {"form": form})


# Admin logout
@login_required
def admin_logout(request):
    logout(request)
    return redirect("home")




class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ["title", "message", "event_date"]
        widgets = {
            "event_date": forms.DateInput(attrs={"type": "date"})
        }


class AdminLoginForm(AuthenticationForm):
    special_code = forms.CharField(
        max_length=50,
        label="Special Code",
        widget=forms.PasswordInput()
    )

    def clean_special_code(self):
        code = self.cleaned_data.get("special_code")
        if not AdminSecretCode.objects.filter(code=code).exists():
            raise forms.ValidationError("Invalid special code. Contact the admin.")
        return code


class GalleryUploadForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ["image", "caption", "category"]
        widgets = {
            "caption": forms.TextInput(attrs={"placeholder": "Optional caption"}),
            "category": forms.Select()
        }

# Optional class-based admin login view
class AdminLoginView(LoginView):
    authentication_form = AdminLoginForm
    template_name = "admin_login.html"

# gallery/forms.py
class BulletinForm(forms.ModelForm):
    fetch_readings = forms.BooleanField(
        required=False,
        help_text="Check this to auto-fetch readings from USCCB"
    )

    class Meta:
        model = Bulletin
        fields = ["date", "title", "reading_1", "responsorial_psalm", "reading_2", "gospel"]

        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "reading_1": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "responsorial_psalm": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "reading_2": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "gospel": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }