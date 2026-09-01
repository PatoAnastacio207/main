{% load static %}/* Service worker for the 2048 site.
 *
 * Served from / (not /static/) on purpose: a worker's scope is limited to the
 * directory it is served from, so one under /static/ could only control
 * /static/*. See the "sw.js" route in 2048/urls.py.
 *
 * Note this only ever runs on a secure origin — HTTPS, or localhost. Over
 * plain http:// on a LAN address the registration below is skipped entirely
 * and the site behaves exactly as it did before.
 */

const VERSION = "v1";
const SHELL_CACHE = `shell-${VERSION}`;
const RUNTIME_CACHE = `runtime-${VERSION}`;

const OFFLINE_URL = "{% url 'offline' %}";

// The minimum needed to render something useful with no network.
const PRECACHE_URLS = [
    OFFLINE_URL,
    "{% static 'blog/blog.css' %}",
    "{% static 'icons/icon-192.png' %}",
    "{% static 'manifest.webmanifest' %}",
];

// Pages that must never be served from cache: they are authentication or
// admin surfaces where a stale copy would be actively misleading.
const NEVER_CACHE = [/^\/admin\//, /^\/login\//, /^\/logout\//, /^\/blog\/new\//];

function isNeverCached(pathname) {
    return NEVER_CACHE.some((re) => re.test(pathname));
}

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches
            .open(SHELL_CACHE)
            .then((cache) => cache.addAll(PRECACHE_URLS))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches
            .keys()
            .then((keys) =>
                Promise.all(
                    keys
                        .filter((key) => key !== SHELL_CACHE && key !== RUNTIME_CACHE)
                        .map((key) => caches.delete(key))
                )
            )
            .then(() => self.clients.claim())
    );
});

self.addEventListener("fetch", (event) => {
    const request = event.request;

    if (request.method !== "GET") return;

    const url = new URL(request.url);
    if (url.origin !== self.location.origin) return;
    if (isNeverCached(url.pathname)) return;

    // Sensor readings must always be live — a cached reading looks current but
    // is not, which is worse than showing nothing.
    if (url.pathname.startsWith("/sensors/latest") || url.pathname.startsWith("/sensors/graph")) {
        return;
    }

    // Static assets change only on redeploy: serve from cache, refresh after.
    if (url.pathname.startsWith("/static/")) {
        event.respondWith(
            caches.match(request).then((cached) => {
                const network = fetch(request)
                    .then((response) => {
                        if (response.ok) {
                            const copy = response.clone();
                            caches.open(RUNTIME_CACHE).then((cache) => cache.put(request, copy));
                        }
                        return response;
                    })
                    .catch(() => cached);
                return cached || network;
            })
        );
        return;
    }

    // Pages: network first, so logged-in state and fresh content always win.
    // Cache is only a fallback for when the network is gone.
    if (request.mode === "navigate") {
        event.respondWith(
            fetch(request)
                .then((response) => {
                    if (response.ok) {
                        const copy = response.clone();
                        caches.open(RUNTIME_CACHE).then((cache) => cache.put(request, copy));
                    }
                    return response;
                })
                .catch(() =>
                    caches
                        .match(request)
                        .then((cached) => cached || caches.match(OFFLINE_URL))
                )
        );
    }
});
