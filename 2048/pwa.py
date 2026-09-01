"""Per-section PWA identities.

Each section of the site installs to the home screen as its own app. On iOS
that is the only mechanism available: Safari has never supported the manifest's
`shortcuts` member, so "long-press the icon for a shortcut" is not something
this site can offer there. What iOS does instead is bookmark whatever URL is
open when you tap Add to Home Screen, taking the name and icon from the tags on
that page. Serving a distinct name, icon and manifest per section therefore
turns one "Add to Home Screen" per section into four separate app icons.

The section is derived from the request path by the context processor below, so
every page under /blog/ (including /blog/3/ and the login page) carries the
blog identity without each template having to declare it.
"""

from django.http import Http404, JsonResponse
from django.templatetags.static import static
from django.urls import reverse

# Keyed by URL prefix. "home" is the fallback for anything not under a section.
APPS = {
    "home": {
        "prefix": "/",
        "name": "2048 — sensores y blog",
        "short_name": "2048",
        # Shown under the icon on the iOS home screen; iOS truncates past ~12
        # characters, so these stay short.
        "title": "2048",
        "url_name": "home",
        "theme_color": "#ffffff",
        "background_color": "#ffffff",
        "status_bar_style": "default",
    },
    "blog": {
        "prefix": "/blog/",
        "name": "2048 Blog",
        "short_name": "Blog",
        "title": "Blog",
        "url_name": "article_list",
        "theme_color": "#ffffff",
        "background_color": "#ffffff",
        "status_bar_style": "default",
    },
    "sensors": {
        "prefix": "/sensors/",
        "name": "Calidad de aire",
        "short_name": "Aire",
        "title": "Aire",
        "url_name": "sensors:dashboard",
        # The dashboard is the one dark page, so it gets a dark status bar.
        "theme_color": "#0f1420",
        "background_color": "#0f1420",
        "status_bar_style": "black",
    },
    "priorities": {
        "prefix": "/priorities/",
        "name": "Priorities",
        "short_name": "Prio",
        "title": "Priorities",
        "url_name": "priorities:list",
        "theme_color": "#ffffff",
        "background_color": "#ffffff",
        "status_bar_style": "default",
    },
}


def slug_for_path(path):
    """Longest matching prefix wins, so "/" only catches what nothing else does."""
    matches = [
        slug
        for slug, app in APPS.items()
        if slug != "home" and path.startswith(app["prefix"])
    ]
    return max(matches, key=lambda slug: len(APPS[slug]["prefix"]), default="home")


def context(request):
    """Template context processor: exposes the current section's PWA identity."""
    slug = slug_for_path(request.path)
    app = APPS[slug]

    return {
        "pwa": {
            "slug": slug,
            "title": app["title"],
            "theme_color": app["theme_color"],
            "status_bar_style": app["status_bar_style"],
            "manifest_url": reverse("pwa_manifest", args=[slug]),
            # iOS ignores the manifest icons and uses the apple-touch-icon link.
            "apple_icon": static(f"icons/{slug}-180.png"),
            "icon": static(f"icons/{slug}-192.png"),
        }
    }


def manifest(request, slug):
    """Serves one section's web app manifest."""
    app = APPS.get(slug)
    if app is None:
        raise Http404(f"No PWA app named {slug!r}")

    start_url = reverse(app["url_name"])

    data = {
        # A distinct id is what makes Chrome treat these as four installable
        # apps rather than four ways of installing the same one.
        "id": start_url,
        "name": app["name"],
        "short_name": app["short_name"],
        "start_url": start_url,
        # Scope stays site-wide even for the section apps. Narrowing it to the
        # section would look tidier but breaks them: /priorities/ and
        # /blog/new/ redirect to the login page at /blog/login/, and an
        # out-of-scope redirect is kicked out into the browser. The first
        # expired session would drop the user out of the app.
        "scope": "/",
        "display": "standalone",
        "background_color": app["background_color"],
        "theme_color": app["theme_color"],
        "icons": [
            {
                "src": static(f"icons/{slug}-192.png"),
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": static(f"icons/{slug}-512.png"),
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": static(f"icons/{slug}-maskable-512.png"),
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "maskable",
            },
        ],
    }

    if slug == "home":
        # Long-press shortcuts on the launcher icon. Android only — Safari
        # ignores this member, which is why each section also has its own app.
        data["shortcuts"] = [
            {
                "name": APPS[section]["name"],
                "short_name": APPS[section]["short_name"],
                "url": reverse(APPS[section]["url_name"]),
                "icons": [
                    {"src": static(f"icons/{section}-192.png"), "sizes": "192x192"}
                ],
            }
            for section in ("sensors", "blog", "priorities")
        ]

    return JsonResponse(data, content_type="application/manifest+json")
