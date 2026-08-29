from django import forms
from django.utils import timezone

from .models import Article


class ArticleForm(forms.ModelForm):
    # Declared explicitly so it can be left blank: an empty date falls back to
    # today rather than blocking the submit.
    date = forms.DateField(
        required=False,
        initial=timezone.localdate,
        # An <input type="date"> only accepts ISO format. Without this, Django
        # renders the localized form ("August 29, 2026"), the browser rejects
        # it, and the field shows up blank.
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )

    def clean_date(self):
        return self.cleaned_data.get("date") or timezone.localdate()

    class Meta:
        model = Article
        fields = [
            "title",
            "title_img",
            "content",
            "summary",
            "keywords",
            "date",
            "status",
        ]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 15}),
            "summary": forms.Textarea(attrs={"rows": 4}),
        }
        help_texts = {
            "content": "Allowed tags: b, i, u, em, strong, mark, small, sub, sup, abbr, span, br. All other tags are stripped on save.",
            "keywords": "Comma-separated, e.g: django, python, web",
        }
