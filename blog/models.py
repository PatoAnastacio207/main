import bleach
from django.contrib.auth.models import User
from django.db import models

ALLOWED_TAGS = [
    "b",
    "i",
    "u",
    "s",
    "em",
    "strong",
    "mark",
    "small",
    "sub",
    "sup",
    "abbr",
    "span",
    "br",
]

ALLOWED_ATTRIBUTES = {
    "abbr": ["title"],
    "span": ["style"],
}

ALLOWED_STYLES = [
    "color",
    "background-color",
    "font-weight",
    "font-style",
    "text-decoration",
]


class Article(models.Model):
    class Status(models.TextChoices):
        PUBLISHED = "published", "Published"
        DRAFT = "draft", "Draft"
        PRIVATE = "private", "Private"

    title = models.CharField(max_length=255)
    title_img = models.ImageField(upload_to="articles/images/", blank=True, null=True)
    content = models.TextField(
        help_text="Only styling tags are allowed (b, i, u, em, strong, span, etc.)"
    )
    summary = models.TextField()
    keywords = models.CharField(max_length=500, help_text="Comma-separated keywords")
    date = models.DateField()
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="articles"
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.DRAFT
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.title} [{self.status}]"

    def save(self, *args, **kwargs):
        # Sanitize content to only allow styling tags before saving
        self.content = bleach.clean(
            self.content,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True,
        )
        super().save(*args, **kwargs)

    def keywords_list(self):
        return [kw.strip() for kw in self.keywords.split(",") if kw.strip()]
