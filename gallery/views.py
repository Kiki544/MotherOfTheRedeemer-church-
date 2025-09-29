from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from .models import GalleryImage, Announcement, AdminSecretCode, Bulletin
from .forms import AnnouncementForm, AdminLoginForm, GalleryUploadForm, BulletinForm
import requests
from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404, render, redirect
from datetime import date
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re
import html


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
        return redirect("gallery")  
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

    def dispatch(self, request, *args, **kwargs):
        # If user is already logged in, redirect to home
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Extra check for special code
        code = form.cleaned_data.get("special_code")
        if not AdminSecretCode.objects.filter(code=code).exists():
            form.add_error("special_code", "Invalid special code")
            return self.form_invalid(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        # Show error message if login fails
        messages.error(self.request, "Invalid username, password, or special code.")
        return super().form_invalid(form)

def fetch_daily_reading(bulletin_date):
    date_str = bulletin_date.strftime("%Y%m%d")
    url = f"https://universalis.com/usa/{date_str}/jsonpmass.js?callback=universalisCallback"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        if hasattr(response, 'status_code') and response.status_code == 404:
            return {"error": f"Readings for {bulletin_date} not yet published."}
        return {"error": f"HTTP Error: {e}"}

    text = response.text
    match = re.search(r"universalisCallback\((.*)\);", text, re.DOTALL)
    if not match:
        return {"error": "Could not parse JSONP response"}

    try:
        data = json.loads(match.group(1))
    except Exception as e:
        return {"error": f"JSON decode error: {str(e)}"}

    readings = {}

    # Helper: prefer HTML 'content' if available, otherwise fallback to 'text'
    def get_text(block):
        return block.get("content") or block.get("text", "")

    if "Mass_R1" in data:
        r1 = data["Mass_R1"]
        readings["reading_1"] = get_text(r1)
        readings["reading_1_citation"] = r1.get("source", "")

    if "Mass_Ps" in data:
        ps = data["Mass_Ps"]
        readings["responsorial_psalm"] = get_text(ps)
        readings["psalm_refrain"] = ps.get("refrain", "")
        readings["psalm_citation"] = ps.get("source", "")

    if "Mass_R2" in data:
        r2 = data["Mass_R2"]
        readings["reading_2"] = get_text(r2)
        readings["reading_2_citation"] = r2.get("source", "")

    if "Mass_G" in data:
        g = data["Mass_G"]
        readings["gospel"] = get_text(g)
        readings["gospel_citation"] = g.get("source", "")

    # Optionals
    if "Mass_R1_Optional" in data:
        r1_opt = data["Mass_R1_Optional"]
        readings["reading_1_optional"] = get_text(r1_opt)
        readings["reading_1_optional_citation"] = r1_opt.get("source", "")

    if "Mass_Ps_Optional" in data:
        ps_opt = data["Mass_Ps_Optional"]
        readings["psalm_optional"] = get_text(ps_opt)
        readings["psalm_optional_refrain"] = ps_opt.get("refrain", "")
        readings["psalm_optional_citation"] = ps_opt.get("source", "")

    if "Mass_R2_Optional" in data:
        r2_opt = data["Mass_R2_Optional"]
        readings["reading_2_optional"] = get_text(r2_opt)
        readings["reading_2_optional_citation"] = r2_opt.get("source", "")

    if "Mass_G_Optional" in data:
        g_opt = data["Mass_G_Optional"]
        readings["gospel_optional"] = get_text(g_opt)
        readings["gospel_optional_citation"] = g_opt.get("source", "")

    readings["day_title"] = data.get("day", "")
    readings["season"] = data.get("season", "")
    readings["memorial"] = data.get("memorial", "")

    return readings


# Bulletin detail view
def bulletin_detail(request, pk):
    bulletin = get_object_or_404(Bulletin, pk=pk)
    return render(request, "bulletin_detail.html", {"bulletin": bulletin})


@login_required
@csrf_exempt
def bulletin_update_readings(request, pk):
    if request.method == "POST":
        try:
            bulletin = Bulletin.objects.get(pk=pk)
        except Bulletin.DoesNotExist:
            return JsonResponse({"success": False, "error": "Bulletin not found."})

        try:
            data = json.loads(request.body)
            action = data.get("action")
            field = data.get("field")
        except Exception as e:
            return JsonResponse({"success": False, "error": f"Invalid request data: {e}"})

        if action == "delete":
            setattr(bulletin, field, "")
            bulletin.save()
            return JsonResponse({"success": True, "field": field, "content": ""})

        elif action == "refetch":
            readings = fetch_daily_reading(bulletin.date)
            if "error" in readings:
                return JsonResponse({"success": False, "error": readings["error"]})

            new_content = readings.get(field, "")
            setattr(bulletin, field, new_content)
            bulletin.save()
            return JsonResponse({"success": True, "field": field, "content": new_content})

    return JsonResponse({"success": False, "error": "Invalid request method."})

# List all bulletins
def bulletin_list(request):
    bulletins = Bulletin.objects.all().order_by("-date")
    return render(request, "bulletin_list.html", {"bulletins": bulletins})


# Add a new bulletin
@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def bulletin_add(request):
    if request.method == "POST":
        form = BulletinForm(request.POST)
        if form.is_valid():
            bulletin = form.save(commit=False)

            # Auto-fetch readings if checkbox ticked
            if form.cleaned_data.get("fetch_readings"):
                readings = fetch_daily_reading(bulletin.date)
                if "error" not in readings:
                    bulletin.reading_1 = readings.get("reading_1", "")
                    bulletin.responsorial_psalm = readings.get("responsorial_psalm", "")
                    bulletin.reading_2 = readings.get("reading_2", "")
                    bulletin.gospel = readings.get("gospel", "")

            bulletin.save()
            return redirect("bulletin_list")
    else:
        form = BulletinForm()

    return render(request, "bulletin_form.html", {"form": form})
