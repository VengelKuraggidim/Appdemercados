// Service Worker for PWA com Network-First Strategy
const CACHE_VERSION = 'v2.0.01-' + Date.now(); // Versão única baseada em timestamp
const CACHE_NAME = `comparador-precos-${CACHE_VERSION}`;

// Recursos estáticos que podem usar cache agressivo
const STATIC_CACHE_URLS = [
  '/manifest.json'
];

// Estratégias de cache por tipo de recurso
const CACHE_STRATEGIES = {
  // Network-First: Sempre tenta buscar da rede primeiro (JS, CSS, HTML)
  networkFirst: (request) => {
    return fetch(request)
      .then((response) => {
        if (response && response.status === 200) {
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseToCache);
          });
        }
        return response;
      })
      .catch(() => {
        return caches.match(request);
      });
  },

  // Cache-First: Usa cache primeiro (imagens, fontes, etc)
  cacheFirst: (request) => {
    return caches.match(request)
      .then((response) => {
        if (response) {
          return response;
        }
        return fetch(request).then((response) => {
          if (response && response.status === 200) {
            const responseToCache = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseToCache);
            });
          }
          return response;
        });
      });
  }
};

// Install event
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Cache criado -', CACHE_NAME);
        return cache.addAll(STATIC_CACHE_URLS);
      })
      .then(() => {
        console.log('Service Worker: Instalado e pulando espera');
        return self.skipWaiting();
      })
  );
});

// Activate event
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Ativando nova versão');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && cacheName.startsWith('comparador-precos-')) {
            console.log('Service Worker: Removendo cache antigo -', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Service Worker: Assumindo controle de todos os clientes');
      return self.clients.claim();
    })
  );
});

// Fetch event com estratégia inteligente
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Ignora requisições de outros domínios
  if (url.origin !== location.origin) {
    return;
  }

  // IMPORTANTE: Ignora requisições POST, PUT, DELETE (não podem ser cacheadas)
  if (event.request.method !== 'GET') {
    return;
  }

  // IMPORTANTE: Nunca cacheia páginas HTML e JS (sempre busca da rede)
  if (url.pathname.includes('.html') || url.pathname === '/' || url.pathname.includes('.js')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // Determina a estratégia baseada no tipo de arquivo
  const isStaticAsset = /\.(png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot)$/i.test(url.pathname);
  const isCodeFile = /\.(jsx|ts|tsx|css)$/i.test(url.pathname);

  if (isCodeFile) {
    // Network-First para arquivos de código: sempre busca atualização
    event.respondWith(CACHE_STRATEGIES.networkFirst(event.request));
  } else if (isStaticAsset) {
    // Cache-First para assets estáticos
    event.respondWith(CACHE_STRATEGIES.cacheFirst(event.request));
  } else {
    // Network-First como padrão para outros recursos
    event.respondWith(CACHE_STRATEGIES.networkFirst(event.request));
  }
});

// Mensagem para forçar atualização quando solicitado
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    console.log('Service Worker: Forçando ativação imediata');
    self.skipWaiting();
  }
});
