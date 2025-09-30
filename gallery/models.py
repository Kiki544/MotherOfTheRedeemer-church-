from django.db import models
from PIL import Image
from django.db import models
from io import BytesIO
from django.core.files.base import ContentFile

# class GalleryImage(models.Model):
#     CATEGORY_CHOICES = [
#         ("general", "General Gallery"),
#         ("thanksgiving", "Thanksgiving"),
#     ]
#     image = models.ImageField(upload_to="gallery/")
#     caption = models.CharField(max_length=255, blank=True)
#     category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="general")
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.caption} ({self.category})"



class GalleryImage(models.Model):
    CATEGORY_CHOICES = [
        ("general", "General Gallery"),
        ("thanksgiving", "Thanksgiving"),
    ]
    image = models.ImageField(upload_to="gallery/")
    caption = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="general")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.caption} ({self.category})"

    def save(self, *args, **kwargs):
        """Resize and compress uploaded images before saving."""
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        #  Resize to max 1200px (keeps aspect ratio)
        max_size = (1200, 1200)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        #  Save compressed (quality=80 gives good balance)
        img.save(self.image.path, format="JPEG", quality=80, optimize=True)


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    event_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title


class AdminSecretCode(models.Model):
    code = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Admin Code (last updated {self.updated_at:%Y-%m-%d %H:%M})"

    class Meta:
        verbose_name = "Admin Secret Code"
        verbose_name_plural = "Admin Secret Code"



class Bulletin(models.Model):
    date = models.DateField(unique=True)
    title = models.CharField(max_length=200, blank=True)

    # Main Readings
    reading_1 = models.TextField(blank=True, null=True)
    reading_1_citation = models.CharField(max_length=200, blank=True, null=True)
    responsorial_psalm = models.TextField(blank=True, null=True)
    psalm_refrain = models.CharField(max_length=300, blank=True, null=True)
    psalm_citation = models.CharField(max_length=200, blank=True, null=True)
    reading_2 = models.TextField(blank=True, null=True)
    reading_2_citation = models.CharField(max_length=200, blank=True, null=True)
    gospel = models.TextField(blank=True, null=True)
    gospel_citation = models.CharField(max_length=200, blank=True, null=True)

    # Optional Memorial Readings
    reading_1_optional = models.TextField(blank=True, null=True)
    reading_1_optional_citation = models.CharField(max_length=200, blank=True, null=True)
    psalm_optional = models.TextField(blank=True, null=True)
    psalm_optional_refrain = models.CharField(max_length=300, blank=True, null=True)
    psalm_optional_citation = models.CharField(max_length=200, blank=True, null=True)
    reading_2_optional = models.TextField(blank=True, null=True)
    reading_2_optional_citation = models.CharField(max_length=200, blank=True, null=True)
    gospel_optional = models.TextField(blank=True, null=True)
    gospel_optional_citation = models.CharField(max_length=200, blank=True, null=True)

    # Liturgical Info
    day_title = models.CharField(max_length=200, blank=True, null=True)
    season = models.CharField(max_length=200, blank=True, null=True)
    memorial = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bulletin - {self.date}"

