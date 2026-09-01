from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TaskForm
from .models import Task


def _pending():
    """Completed tasks are invisible: this is the only queryset the UI sees."""
    return Task.objects.filter(completed_at__isnull=True)


@staff_member_required(login_url="login")
def task_list(request):
    """Lists pending tasks and creates new ones."""
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("priorities:list")
    else:
        form = TaskForm()

    return render(
        request,
        "task_list.html",
        {"tasks": _pending(), "form": form},
    )


@staff_member_required(login_url="login")
def task_action(request, pk):
    """Applies one action to a task: move it up or down, or complete it."""
    if request.method != "POST":
        return redirect("priorities:list")

    task = get_object_or_404(_pending(), pk=pk)
    action = request.POST.get("action")

    if action == "complete":
        task.complete()
    elif action in ("up", "down"):
        _move(task, -1 if action == "up" else 1)

    return redirect("priorities:list")


def _move(task, delta):
    """Moves a task one position and renumbers the list.

    Renumbering the whole list rather than swapping two values keeps this
    correct even when several tasks share an order — which they do for any
    task created before this app assigned positions, or edited in the admin.
    """
    with transaction.atomic():
        tasks = list(_pending().select_for_update())
        index = next((i for i, t in enumerate(tasks) if t.pk == task.pk), None)
        if index is None:
            return

        target = index + delta
        if not 0 <= target < len(tasks):
            return

        tasks.insert(target, tasks.pop(index))
        for position, item in enumerate(tasks):
            item.order = position
        Task.objects.bulk_update(tasks, ["order"])
