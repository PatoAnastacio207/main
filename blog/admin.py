from django import forms
from django.contrib import admin
from django.utils import timezone

from .models import Article


class ArticleAdminForm(forms.ModelForm):
    """Mirrors ArticleForm: leaving the date blank means today.

    A model field with a default is still blank=False, so without this the
    admin would reject an empty date even though the model can fill it in.
    """

    class Meta:
        model = Article
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].required = False

    def clean_date(self):
        return self.cleaned_data.get("date") or timezone.localdate()


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    list_display = ["title", "author", "date", "status", "created_at"]
    list_filter = ["status", "date", "author"]
    search_fields = ["title", "summary", "keywords"]
    date_hierarchy = "date"
    readonly_fields = ["created_at", "updated_at"]
