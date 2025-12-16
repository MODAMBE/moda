// ===============================
// Service Worker ModApp
// Optimisé pour offline, cache intelligent, notifications et background sync
// ===============================

// Nom du cache pour ModApp
const CACHE_NAME = "modapp-cache-v1";

// Fichiers essentiels à mettre en cache
const urlsToCache = [
    "/",
    "/static/eglise/css/style.css",
    "/static/eglise/js/script.js",
    "/static/eglise/manifest/modapp1.png",
    "/static/eglise/manifest/modapp2.png",
    // Ajouter ici toutes les pages HTML et fichiers essentiels
];

// -------------------------------
// INSTALLATION : mise en cache des fichiers essentiels
// -------------------------------
self.addEventListener("install", event => {
    console.log("Service Worker ModApp: installation en cours...");
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log("Service Worker ModApp: fichiers en cache");
                return cache.addAll(urlsToCache);
            })
    );
    self.skipWaiting();
});

// -------------------------------
// ACTIVATION : nettoyage des anciens caches
// -------------------------------
self.addEventListener("activate", event => {
    console.log("Service Worker ModApp: activation...");
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys.map(key => {
                    if (key !== CACHE_NAME) {
                        console.log("Service Worker ModApp: suppression ancien cache", key);
                        return caches.delete(key);
                    }
                })
            )
        )
    );
    self.clients.claim();
});

// -------------------------------
// FETCH : intercepter les requêtes pour offline
// Cache-first avec fallback réseau et gestion hors-ligne
// -------------------------------
self.addEventListener("fetch", event => {
    event.respondWith(
        caches.match(event.request).then(cachedResponse => {
            if (cachedResponse) {
                return cachedResponse; // retourne le cache
            }
            return fetch(event.request)
                .then(networkResponse => {
                    return caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, networkResponse.clone()); // met à jour le cache
                        return networkResponse;
                    });
                })
                .catch(() => {
                    // Fallback si hors-ligne
                    if (event.request.destination === "document") {
                        return caches.match("/"); // page d'accueil offline
                    }
                    return new Response("Vous êtes hors ligne", {
                        status: 503,
                        statusText: "Service Unavailable",
                    });
                });
        })
    );
});

// -------------------------------
// PUSH NOTIFICATIONS (optionnel)
// -------------------------------
self.addEventListener("push", event => {
    const data = event.data ? event.data.json() : {
        title: "ModApp",
        body: "Nouvelle notification!"
    };
    self.registration.showNotification(data.title, {
        body: data.body,
        icon: "/static/eglise/manifest/modapp1.png",
        badge: "/static/eglise/manifest/modapp1.png"
    });
});

// -------------------------------
// BACKGROUND SYNC : envoyer des données stockées offline
// -------------------------------
self.addEventListener("sync", event => {
    if (event.tag === "sendDataOffline") {
        event.waitUntil(sendDataToServer());
    }
});

// Fonction pour envoyer des données stockées offline au serveur
async function sendDataToServer() {
    console.log("Service Worker ModApp: synchronisation en arrière-plan...");
    // Implémente ici l'envoi des données locales au serveur
}
