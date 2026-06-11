from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ArticleForm
from .models import Article


def article_list(request):
    """Public view: shows all published articles."""
    articles = Article.objects.filter(status=Article.Status.PUBLISHED)
    return render(request, "article_list.html", {"articles": articles})


def article_detail(request, pk):
    """Public dynamic view: renders a single published article."""
    article = get_object_or_404(Article, pk=pk, status=Article.Status.PUBLISHED)
    return render(request, "article_detail.html", {"article": article})


@staff_member_required
def article_create(request):
    """Admin-only view: form to create a new article."""
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, f'Article "{article.title}" created.')
            return redirect("blog_detail", pk=article.pk)

    else:
        form = ArticleForm()

    return render(request, "article_form.html", {"form": form})
