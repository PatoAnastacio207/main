from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["name", "order", "completed_at", "created_at"]
    list_filter = ["completed_at"]
    search_fields = ["name"]
    readonly_fields = ["created_at"]
