from django import forms

from .models import Article


class ArticleForm(forms.ModelForm):
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
            "date": forms.DateInput(attrs={"type": "date"}),
            "content": forms.Textarea(attrs={"rows": 15}),
            "summary": forms.Textarea(attrs={"rows": 4}),
        }
        help_texts = {
            "content": "Allowed tags: b, i, u, em, strong, mark, small, sub, sup, abbr, span, br. All other tags are stripped on save.",
            "keywords": "Comma-separated, e.g: django, python, web",
        }
