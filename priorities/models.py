from django.db import models
from django.db.models import Max
from django.utils import timezone


class Task(models.Model):
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # New tasks go to the bottom of the list. Done here rather than in the
        # view so tasks added through the admin land in the right place too.
        if self._state.adding and not self.order:
            highest = Task.objects.aggregate(Max("order"))["order__max"] or 0
            self.order = highest + 1
        super().save(*args, **kwargs)

    @property
    def is_completed(self):
        return self.completed_at is not None

    def complete(self):
        self.completed_at = timezone.now()
        self.save(update_fields=["completed_at"])
