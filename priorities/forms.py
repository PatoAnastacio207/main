from django import forms

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "New task",
                    "autofocus": True,
                    "autocomplete": "off",
                }
            )
        }
        labels = {"name": ""}
