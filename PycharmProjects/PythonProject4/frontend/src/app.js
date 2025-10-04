// API Configuration
const API_URL = 'http://localhost:8000';

let selectedMarkets = [];
let deferredPrompt;
let userLocation = null;
let useGeoOptimization = false;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    setupPWA();
    requestUserLocation();
    carregarSupermercados();
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

    // Verificar se usuário está logado (para cobrar tokens)
    const usuarioLogado = localStorage.getItem('usuario_nome');

    // Show loading
    document.getElementById('loading').classList.add('show');
    document.getElementById('results').innerHTML = '';
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('stats').style.display = 'none';
    document.getElementById('searchBtn').disabled = true;

    try {
        let response, data;

        // Se temos localização e busca otimizada está habilitada
        if (userLocation && useGeoOptimization) {
            // Carregar configuração de transporte do localStorage
            const configTransporte = JSON.parse(localStorage.getItem('configTransporte') || '{"tipo":"carro","considerar_tempo":true}');

            const url = usuarioLogado
                ? `${API_URL}/api/buscar-otimizado?termo=${encodeURIComponent(termo)}&latitude=${userLocation.latitude}&longitude=${userLocation.longitude}&tipo_transporte=${configTransporte.tipo}&considerar_tempo=${configTransporte.considerar_tempo}&usuario_nome=${encodeURIComponent(usuarioLogado)}`
                : `${API_URL}/api/buscar-otimizado?termo=${encodeURIComponent(termo)}&latitude=${userLocation.latitude}&longitude=${userLocation.longitude}&tipo_transporte=${configTransporte.tipo}&considerar_tempo=${configTransporte.considerar_tempo}`;

            response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
        } else {
            // Busca normal (com ou sem usuário)
            const url = usuarioLogado
                ? `${API_URL}/api/buscar?usuario_nome=${encodeURIComponent(usuarioLogado)}`
                : `${API_URL}/api/buscar`;

            response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    termo: termo,
                    supermercados: selectedMarkets.length > 0 ? selectedMarkets : null
                })
            });
        }

        data = await response.json();

        // Se erro 402 (Payment Required - saldo insuficiente)
        if (response.status === 402) {
            alert(`❌ ${data.detail.mensagem}\n\n💡 ${data.detail.dica}`);
            document.getElementById('loading').classList.remove('show');
            document.getElementById('searchBtn').disabled = false;
            return;
        }

        if (data.produtos && data.produtos.length > 0) {
            exibirResultados(data.produtos, useGeoOptimization);
            exibirEstatisticas(data.produtos);

            // Mostrar info de tokens gastos se disponível
            if (data.tokens && usuarioLogado) {
                mostrarInfoTokens(data.tokens);
                // Atualizar carteira após gastar tokens
                if (window.atualizarCarteira) {
                    setTimeout(() => window.atualizarCarteira(), 500);
                }
            }
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

function mostrarInfoTokens(tokensInfo) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;

    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 24px;">💰</span>
            <div>
                <div style="font-weight: bold;">-${tokensInfo.tokens_gastos} token</div>
                <div style="font-size: 12px; opacity: 0.9;">Saldo restante: ${tokensInfo.saldo_restante} tokens</div>
            </div>
        </div>
    `;

    document.body.appendChild(notification);

    // Remover após 3 segundos
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function exibirResultados(produtos, comGeolocalizacao = false) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = '';

    // Sort by price (ou por custo_total_real se tiver geolocalização)
    if (comGeolocalizacao && produtos[0]?.custo_total_real) {
        produtos.sort((a, b) => a.custo_total_real - b.custo_total_real);
    } else {
        produtos.sort((a, b) => a.preco - b.preco);
    }

    produtos.forEach((produto, index) => {
        const card = document.createElement('div');
        card.className = 'product-card';

        const promoTag = produto.em_promocao ? '<span class="promo-badge">🔥 PROMOÇÃO</span>' : '';

        let bestPriceTag = '';
        if (comGeolocalizacao && index === 0) {
            bestPriceTag = '<span class="promo-badge" style="background: #4CAF50;">⭐ MELHOR CUSTO-BENEFÍCIO</span>';
        } else if (!comGeolocalizacao && index === 0) {
            bestPriceTag = '<span class="promo-badge" style="background: #4CAF50;">💰 MELHOR PREÇO</span>';
        }

        const dataAtualizacao = produto.data_coleta ? formatarData(produto.data_coleta) : 'Data não disponível';

        // Informações de geolocalização com análise completa
        let geoInfo = '';
        if (comGeolocalizacao && produto.distancia_km !== undefined) {
            const custoDeslocamento = produto.custo_deslocamento?.custo_total || 0;
            const custoTransporte = produto.custo_deslocamento?.custo_transporte || 0;
            const custoTempo = produto.custo_deslocamento?.custo_tempo || 0;
            const tempoMinutos = produto.tempo_estimado_minutos || 0;

            // Se não é o primeiro (melhor), mostrar comparação
            let analiseEconomia = '';
            if (index > 0) {
                const melhorOpcao = produtos[0];
                const diferencaPreco = produto.preco - melhorOpcao.preco;
                const diferencaCustoTotal = produto.custo_total_real - melhorOpcao.custo_total_real;

                if (diferencaCustoTotal > 0.50) {
                    analiseEconomia = `
                        <div class="economia-resumo negativa">
                            ⚠️ Você gastaria R$ ${diferencaCustoTotal.toFixed(2)} a mais aqui
                        </div>
                    `;
                }
            } else {
                // É a melhor opção - mostrar por que
                if (produtos.length > 1) {
                    const segundaOpcao = produtos[1];
                    const economiaReal = segundaOpcao.custo_total_real - produto.custo_total_real;

                    analiseEconomia = `
                        <div class="economia-resumo">
                            ✅ Melhor opção! Economia de R$ ${economiaReal.toFixed(2)} vs. ${getSupermarketName(segundaOpcao.supermercado)}
                        </div>
                    `;
                }
            }

            geoInfo = `
                <div class="economia-info">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <strong style="font-size: 13px;">💰 Análise de Custo-Benefício</strong>
                        <div class="info-tooltip">
                            i
                            <div class="tooltip-content">
                                Cálculo considera: preço + distância (ida/volta) + tempo
                            </div>
                        </div>
                    </div>

                    <div class="economia-detalhes">
                        <div class="economia-linha">
                            <span>📍 Distância:</span>
                            <strong>${produto.distancia_km.toFixed(1)} km</strong>
                        </div>
                        <div class="economia-linha">
                            <span>⏱️ Tempo estimado:</span>
                            <strong>${tempoMinutos.toFixed(0)} min</strong>
                        </div>
                        <div class="economia-linha">
                            <span>🚗 Combustível/Transporte:</span>
                            <strong>R$ ${custoTransporte.toFixed(2)}</strong>
                        </div>
                        <div class="economia-linha">
                            <span>⌚ Custo do tempo:</span>
                            <strong>R$ ${custoTempo.toFixed(2)}</strong>
                        </div>
                        <div class="economia-linha economia-total">
                            <span>💵 Custo Real Total:</span>
                            <strong style="font-size: 15px;">R$ ${produto.custo_total_real.toFixed(2)}</strong>
                        </div>
                    </div>

                    ${analiseEconomia}
                </div>
            `;
        }

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
            ${geoInfo}
            <div style="color: #999; font-size: 13px; margin-top: 10px;">
                📅 Atualizado: ${dataAtualizacao}
            </div>
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
    // Se já é um nome legível (não slug), retornar direto
    if (!slug.includes('_') && slug.length > 3) {
        return slug.charAt(0).toUpperCase() + slug.slice(1);
    }

    const names = {
        'carrefour': 'Carrefour',
        'pao_acucar': 'Pão de Açúcar',
        'extra': 'Extra',
        'mercado_livre': 'Mercado Livre',
        'atacadao': 'Atacadão',
        'loja_descontos': 'Loja dos Descontos',
        'loja_dos_descontos': 'Loja dos Descontos'
    };

    // Se encontrou no mapa, retornar
    if (names[slug.toLowerCase()]) {
        return names[slug.toLowerCase()];
    }

    // Caso contrário, formatar o slug: remove _ e capitaliza
    return slug.split('_').map(word =>
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

function formatarData(dataString) {
    try {
        const data = new Date(dataString);
        const agora = new Date();
        const diffMs = agora - data;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHoras = Math.floor(diffMs / 3600000);
        const diffDias = Math.floor(diffMs / 86400000);

        if (diffMins < 1) {
            return 'Agora mesmo';
        } else if (diffMins < 60) {
            return `${diffMins} min atrás`;
        } else if (diffHoras < 24) {
            return `${diffHoras}h atrás`;
        } else if (diffDias === 1) {
            return 'Ontem';
        } else if (diffDias < 7) {
            return `${diffDias} dias atrás`;
        } else {
            return data.toLocaleDateString('pt-BR');
        }
    } catch (e) {
        return 'Data não disponível';
    }
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

// ============================================
// GEOLOCALIZAÇÃO
// ============================================

function requestUserLocation() {
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                };
                console.log('Localização obtida:', userLocation);
                showGeoLocationUI();
            },
            (error) => {
                console.warn('Erro ao obter localização:', error);
                // Continua funcionando sem geolocalização
            }
        );
    }
}

function showGeoLocationUI() {
    // Adiciona toggle para habilitar busca otimizada
    const searchContainer = document.querySelector('.search-box');

    if (!searchContainer) {
        console.warn('search-box não encontrado');
        return;
    }

    if (!document.getElementById('geoToggle')) {
        const geoToggle = document.createElement('div');
        geoToggle.id = 'geoToggle';
        geoToggle.style.cssText = `
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 10px;
            padding: 10px;
            background: #e8f5e9;
            border-radius: 8px;
            font-size: 14px;
        `;

        geoToggle.innerHTML = `
            <input type="checkbox" id="geoOptimizationCheckbox" />
            <label for="geoOptimizationCheckbox" style="cursor: pointer;">
                📍 Buscar considerando distância e custo de deslocamento
            </label>
        `;

        searchContainer.appendChild(geoToggle);

        document.getElementById('geoOptimizationCheckbox').addEventListener('change', (e) => {
            useGeoOptimization = e.target.checked;
            console.log('Otimização geográfica:', useGeoOptimization ? 'Ativada' : 'Desativada');
        });
    }
}

function toggleGeoOptimization(enabled) {
    useGeoOptimization = enabled;
}

// Carregar supermercados dinamicamente do banco
async function carregarSupermercados() {
    try {
        const response = await fetch(`${API_URL}/api/supermercados-contribuidos`);
        if (response.ok) {
            const data = await response.json();

            const filtersContainer = document.getElementById('supermarketFilters');
            if (!filtersContainer) return;

            // Manter apenas o botão "Todos"
            filtersContainer.innerHTML = '<div class="filter-chip active" data-market="all">Todos</div>';

            // Adicionar supermercados do banco
            data.supermercados.forEach(super_ => {
                const chip = document.createElement('div');
                chip.className = 'filter-chip';
                chip.dataset.market = super_.nome.toLowerCase().replace(/\s+/g, '_');
                chip.textContent = super_.nome;

                chip.addEventListener('click', () => {
                    toggleMarketFilter(chip);
                });

                filtersContainer.appendChild(chip);
            });

            console.log(`✅ ${data.supermercados.length} supermercados carregados`);
        }
    } catch (error) {
        console.error('Erro ao carregar supermercados:', error);
    }
}
