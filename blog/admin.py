from django.contrib import admin

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "date", "status", "created_at"]
    list_filter = ["status", "date", "author"]
    search_fields = ["title", "summary", "keywords"]
    date_hierarchy = "date"
    readonly_fields = ["created_at", "updated_at"]
