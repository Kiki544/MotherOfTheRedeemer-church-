from django.db import models

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
