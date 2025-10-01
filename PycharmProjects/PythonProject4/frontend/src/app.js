// API Configuration
const API_URL = 'http://localhost:8000';

let selectedMarkets = [];
let deferredPrompt;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    setupPWA();
});

function setupEventListeners() {
    // Search on Enter key
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            buscarProdutos();
        }
    });

    // Supermarket filters
    document.querySelectorAll('.filter-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            toggleMarketFilter(chip);
        });
    });
}

function toggleMarketFilter(chip) {
    const market = chip.dataset.market;

    if (market === 'all') {
        // Select all
        document.querySelectorAll('.filter-chip').forEach(c => {
            c.classList.remove('active');
        });
        chip.classList.add('active');
        selectedMarkets = [];
    } else {
        // Toggle individual market
        document.querySelector('.filter-chip[data-market="all"]').classList.remove('active');
        chip.classList.toggle('active');

        if (chip.classList.contains('active')) {
            selectedMarkets.push(market);
        } else {
            selectedMarkets = selectedMarkets.filter(m => m !== market);
        }

        // If none selected, select all
        if (selectedMarkets.length === 0) {
            document.querySelector('.filter-chip[data-market="all"]').classList.add('active');
        }
    }
}

async function buscarProdutos() {
    const termo = document.getElementById('searchInput').value.trim();

    if (!termo || termo.length < 2) {
        alert('Digite pelo menos 2 caracteres para buscar');
        return;
    }

    // Show loading
    document.getElementById('loading').classList.add('show');
    document.getElementById('results').innerHTML = '';
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('stats').style.display = 'none';
    document.getElementById('searchBtn').disabled = true;

    try {
        const response = await fetch(`${API_URL}/api/buscar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                termo: termo,
                supermercados: selectedMarkets.length > 0 ? selectedMarkets : null
            })
        });

        const data = await response.json();

        if (data.produtos && data.produtos.length > 0) {
            exibirResultados(data.produtos);
            exibirEstatisticas(data.produtos);
        } else {
            document.getElementById('emptyState').innerHTML = `
                <p>😕 Nenhum produto encontrado para "${termo}"</p>
                <p style="font-size: 14px; margin-top: 10px;">Tente buscar com outros termos</p>
            `;
            document.getElementById('emptyState').style.display = 'block';
        }
    } catch (error) {
        console.error('Erro ao buscar produtos:', error);
        alert('Erro ao buscar produtos. Verifique se o servidor está rodando.');
    } finally {
        document.getElementById('loading').classList.remove('show');
        document.getElementById('searchBtn').disabled = false;
    }
}

function exibirResultados(produtos) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = '';

    // Sort by price
    produtos.sort((a, b) => a.preco - b.preco);

    produtos.forEach((produto, index) => {
        const card = document.createElement('div');
        card.className = 'product-card';

        const promoTag = produto.em_promocao ? '<span class="promo-badge">🔥 PROMOÇÃO</span>' : '';
        const bestPriceTag = index === 0 ? '<span class="promo-badge" style="background: #4CAF50;">💰 MELHOR PREÇO</span>' : '';

        card.innerHTML = `
            <div class="product-name">${produto.nome}</div>
            ${produto.marca ? `<div style="color: #666; font-size: 14px; margin-bottom: 10px;">${produto.marca}</div>` : ''}
            <div class="product-details">
                <div>
                    <div class="price">R$ ${produto.preco.toFixed(2)}</div>
                    ${promoTag}
                    ${bestPriceTag}
                </div>
                <div>
                    <span class="supermarket-badge">${getSupermarketName(produto.supermercado)}</span>
                </div>
            </div>
            ${produto.url ? `<a href="${produto.url}" target="_blank" class="product-link">Ver no site →</a>` : ''}
        `;

        resultsContainer.appendChild(card);
    });
}

function exibirEstatisticas(produtos) {
    const statsDiv = document.getElementById('stats');
    statsDiv.style.display = 'grid';

    const precos = produtos.map(p => p.preco);
    const melhorPreco = Math.min(...precos);
    const piorPreco = Math.max(...precos);
    const economia = piorPreco - melhorPreco;

    document.getElementById('totalProdutos').textContent = produtos.length;
    document.getElementById('melhorPreco').textContent = `R$ ${melhorPreco.toFixed(2)}`;
    document.getElementById('economia').textContent = `R$ ${economia.toFixed(2)}`;
}

function getSupermarketName(slug) {
    const names = {
        'carrefour': 'Carrefour',
        'pao_acucar': 'Pão de Açúcar',
        'extra': 'Extra',
        'mercado_livre': 'Mercado Livre',
        'atacadao': 'Atacadão'
    };
    return names[slug] || slug;
}

// PWA Setup
function setupPWA() {
    // Register service worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(reg => console.log('Service Worker registered'))
            .catch(err => console.log('Service Worker registration failed:', err));
    }

    // Install prompt
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        document.getElementById('installPrompt').classList.add('show');
    });
}

function instalarApp() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('App instalado');
            }
            deferredPrompt = null;
            fecharInstall();
        });
    }
}

function fecharInstall() {
    document.getElementById('installPrompt').classList.remove('show');
}
