// Scanner de Nota Fiscal
const API_URL = 'http://localhost:8000';

let selectedFile = null;

// Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const previewSection = document.getElementById('previewSection');
const previewImage = document.getElementById('previewImage');
const scanBtn = document.getElementById('scanBtn');
const debugBtn = document.getElementById('debugBtn'); // pode ser null
const loading = document.getElementById('loading');
const resultSection = document.getElementById('resultSection');
const errorMessage = document.getElementById('errorMessage');

// Event Listeners
console.log('Configurando eventos do scanner...');

if (uploadArea) {
    uploadArea.addEventListener('click', () => {
        console.log('Upload area clicada');
        fileInput.click();
    });
    console.log('✓ Click event configurado');
} else {
    console.error('uploadArea não encontrado!');
}

if (fileInput) {
    fileInput.addEventListener('change', (e) => {
        console.log('Input file changed, arquivos:', e.target.files.length);
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
    console.log('✓ Change event configurado');
} else {
    console.error('fileInput não encontrado!');
}

// Drag and Drop
if (uploadArea) {
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.classList.add('dragging');
        console.log('Dragging over...');
    });

    uploadArea.addEventListener('dragenter', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.classList.add('dragging');
    });

    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.classList.remove('dragging');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.classList.remove('dragging');

        console.log('Drop event!');
        console.log('DataTransfer:', e.dataTransfer);
        console.log('Files:', e.dataTransfer.files);
        console.log('Files length:', e.dataTransfer.files.length);

        // Tentar pegar arquivo de diferentes formas
        let file = null;

        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            file = e.dataTransfer.files[0];
            console.log('Arquivo via files:', file);
        } else if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
            // Tentar via items API
            const item = e.dataTransfer.items[0];
            if (item.kind === 'file') {
                file = item.getAsFile();
                console.log('Arquivo via items:', file);
            }
        }

        if (file) {
            console.log('✓ Arquivo capturado:', file.name, file.type, file.size);
            handleFileSelect(file);
        } else {
            console.error('❌ Nenhum arquivo capturado no drop');
            showError('Não foi possível ler o arquivo. Tente clicar e selecionar.');
        }
    });
    console.log('✓ Drag and drop configurado');
}

if (scanBtn) {
    scanBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        await processarNotaFiscal();
    });
}

if (debugBtn) {
    debugBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        await debugOCR();
    });
}

function handleFileSelect(file) {
    if (!file) {
        console.log('Nenhum arquivo selecionado');
        return;
    }

    console.log('Arquivo selecionado:', file.name, file.type, file.size);

    // Validar tipo - aceitar qualquer imagem
    const isImage = file.type.startsWith('image/') ||
                    file.name.match(/\.(jpg|jpeg|png|gif|bmp|webp)$/i);

    if (!isImage) {
        showError('Por favor, selecione uma imagem válida (JPG, PNG, etc.)');
        return;
    }

    // Validar tamanho (10MB)
    if (file.size > 10 * 1024 * 1024) {
        showError('Imagem muito grande. Máximo 10MB');
        return;
    }

    selectedFile = file;
    console.log('Arquivo aceito e armazenado');

    // Mostrar preview
    const reader = new FileReader();
    reader.onload = (e) => {
        if (previewImage) previewImage.src = e.target.result;
        if (previewSection) previewSection.style.display = 'block';
        if (scanBtn) scanBtn.disabled = false;
        if (debugBtn) debugBtn.disabled = false;
        console.log('Preview carregado, botões habilitados');
    };
    reader.onerror = (e) => {
        console.error('Erro ao ler arquivo:', e);
        showError('Erro ao ler arquivo. Tente outro arquivo.');
    };
    reader.readAsDataURL(file);
}

async function processarNotaFiscal() {
    // Verificar se usuário está logado
    const usuarioLogado = localStorage.getItem('usuario_nome');

    if (!usuarioLogado || usuarioLogado === 'null' || usuarioLogado === '') {
        showError('❌ Você precisa estar logado para escanear notas fiscais. Faça login na página principal primeiro.');
        if (scanBtn) scanBtn.disabled = false;
        return;
    }

    console.log('Usuário logado:', usuarioLogado);

    // Perguntar qual modo de OCR usar
    const modo = await perguntarModoOCR();
    if (!modo) return; // Usuário cancelou

    // Criar FormData
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('usuario_nome', usuarioLogado);
    formData.append('modo', modo);

    // DEBUG: Verificar FormData
    console.log('=== DEBUG FormData ===');
    console.log('Usuario logado:', usuarioLogado);
    console.log('Modo OCR:', modo);
    console.log('Arquivo:', selectedFile?.name);
    for (let pair of formData.entries()) {
        console.log(pair[0] + ':', pair[1]);
    }
    console.log('=====================');

    // Mostrar loading
    loading.classList.add('show');
    if (scanBtn) scanBtn.disabled = true;
    errorMessage.classList.remove('show');

    console.log('Enviando requisição para:', `${API_URL}/api/ocr-inteligente`);

    try {
        const response = await fetch(`${API_URL}/api/ocr-inteligente`, {
            method: 'POST',
            body: formData
        });

        console.log('Resposta recebida:', response.status);

        const data = await response.json();

        if (!data.sucesso) {
            showError(data.mensagem || data.erro || 'Erro ao processar nota fiscal');
            return;
        }

        // Adaptar dados para mostrar resultados
        const dadosAdaptados = {
            sucesso: true,
            supermercado: data.dados_extraidos.supermercado || 'Supermercado',
            total_produtos: data.produtos_adicionados,
            data_compra: data.dados_extraidos.data_compra,
            total_nota: data.dados_extraidos.total,
            soma_produtos: data.produtos.reduce((sum, p) => sum + p.preco, 0),
            produtos_salvos: data.produtos,
            tokens_ganhos: data.tokens_ganhos,
            engine_usada: data.engine_usada,
            confianca: data.confianca
        };

        // Mostrar resultados
        mostrarResultados(dadosAdaptados);

        // Mostrar mensagem de sucesso com info da engine
        mostrarMensagemSucessoComEngine(dadosAdaptados);

    } catch (error) {
        console.error('Erro:', error);
        showError('Erro ao processar nota fiscal. Verifique se o servidor está rodando.');
    } finally {
        loading.classList.remove('show');
    }
}

async function perguntarModoOCR() {
    return new Promise((resolve) => {
        // Criar modal de seleção
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.7);
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        `;

        modal.innerHTML = `
            <div style="background: white; max-width: 500px; border-radius: 16px; padding: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.3);">
                <h2 style="margin: 0 0 20px 0; color: #333;">🔍 Escolha o Modo de OCR</h2>

                <div style="display: flex; flex-direction: column; gap: 15px;">
                    <!-- Modo Grátis -->
                    <button id="modo-gratis" style="
                        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                        color: white;
                        border: none;
                        padding: 20px;
                        border-radius: 12px;
                        cursor: pointer;
                        text-align: left;
                        transition: transform 0.2s;
                    " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
                        <div style="font-size: 18px; font-weight: bold; margin-bottom: 5px;">
                            💚 Grátis (EasyOCR)
                        </div>
                        <div style="font-size: 14px; opacity: 0.9;">
                            100% grátis, offline, ~70% precisão
                        </div>
                        <div style="font-size: 12px; opacity: 0.8; margin-top: 5px;">
                            ✅ Sem custos | ⚡ Rápido (5s)
                        </div>
                    </button>

                    <!-- Modo Automático -->
                    <button id="modo-auto" style="
                        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
                        color: white;
                        border: none;
                        padding: 20px;
                        border-radius: 12px;
                        cursor: pointer;
                        text-align: left;
                        transition: transform 0.2s;
                    " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
                        <div style="font-size: 18px; font-weight: bold; margin-bottom: 5px;">
                            🤖 Automático (Recomendado)
                        </div>
                        <div style="font-size: 14px; opacity: 0.9;">
                            Sistema escolhe o melhor OCR automaticamente
                        </div>
                        <div style="font-size: 12px; opacity: 0.8; margin-top: 5px;">
                            ✅ Melhor custo-benefício | 🎯 Precisão alta
                        </div>
                    </button>

                    <!-- Modo Premium -->
                    <button id="modo-premium" style="
                        background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
                        color: white;
                        border: none;
                        padding: 20px;
                        border-radius: 12px;
                        cursor: pointer;
                        text-align: left;
                        transition: transform 0.2s;
                    " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
                        <div style="font-size: 18px; font-weight: bold; margin-bottom: 5px;">
                            ⭐ Premium (Claude Vision)
                        </div>
                        <div style="font-size: 14px; opacity: 0.9;">
                            Máxima precisão com IA da Anthropic
                        </div>
                        <div style="font-size: 12px; opacity: 0.8; margin-top: 5px;">
                            💰 ~R$ 0,20/nota | 🎯 ~99% precisão
                        </div>
                    </button>

                    <button id="modo-cancelar" style="
                        background: #f5f5f5;
                        color: #666;
                        border: none;
                        padding: 15px;
                        border-radius: 8px;
                        cursor: pointer;
                        margin-top: 10px;
                    ">
                        Cancelar
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Event listeners
        document.getElementById('modo-gratis').onclick = () => {
            modal.remove();
            resolve('gratis');
        };

        document.getElementById('modo-auto').onclick = () => {
            modal.remove();
            resolve(null); // null = automático
        };

        document.getElementById('modo-premium').onclick = () => {
            modal.remove();
            resolve('premium');
        };

        document.getElementById('modo-cancelar').onclick = () => {
            modal.remove();
            resolve(null);
            if (scanBtn) scanBtn.disabled = false;
        };
    });
}

function mostrarMensagemSucessoComEngine(data) {
    // Criar notificação de sucesso
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 20px 30px;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideInRight 0.5s ease-out;
        max-width: 400px;
    `;

    const produtosTexto = data.total_produtos === 1 ? '1 produto' : `${data.total_produtos} produtos`;
    const tokensTexto = data.tokens_ganhos ? `<div style="font-size: 16px; margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.3);">💎 +${data.tokens_ganhos} tokens ganhos!</div>` : '';

    const engineInfo = data.engine_usada ? `<div style="font-size: 12px; margin-top: 5px; opacity: 0.8;">🤖 ${data.engine_usada} ${data.confianca ? `(${data.confianca.toFixed(1)}%)` : ''}</div>` : '';

    notification.innerHTML = `
        <div style="display: flex; align-items: start; gap: 15px;">
            <div style="font-size: 32px;">✅</div>
            <div style="flex: 1;">
                <div style="font-size: 18px; font-weight: bold; margin-bottom: 5px;">
                    Nota Escaneada com Sucesso!
                </div>
                <div style="font-size: 14px; opacity: 0.9;">
                    ${produtosTexto} salvos no banco de dados
                </div>
                ${engineInfo}
                ${tokensTexto}
            </div>
        </div>
    `;

    // Adicionar estilo de animação
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    document.body.appendChild(notification);

    // Remover após 5 segundos
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.5s ease-in';
        setTimeout(() => notification.remove(), 500);
    }, 5000);
}

function mostrarMensagemSucesso(data) {
    // Criar notificação de sucesso
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 20px 30px;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideInRight 0.5s ease-out;
        max-width: 400px;
    `;

    const produtosTexto = data.total_produtos === 1 ? '1 produto' : `${data.total_produtos} produtos`;
    const tokensTexto = data.tokens_ganhos ? `<div style="font-size: 16px; margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.3);">💎 +${data.tokens_ganhos} tokens ganhos!</div>` : '';

    notification.innerHTML = `
        <div style="display: flex; align-items: start; gap: 15px;">
            <div style="font-size: 32px;">✅</div>
            <div style="flex: 1;">
                <div style="font-size: 18px; font-weight: bold; margin-bottom: 5px;">
                    Nota Escaneada com Sucesso!
                </div>
                <div style="font-size: 14px; opacity: 0.9;">
                    ${produtosTexto} salvos no banco de dados
                </div>
                ${tokensTexto}
            </div>
        </div>
    `;

    // Adicionar estilo de animação
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    document.body.appendChild(notification);

    // Remover após 5 segundos
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.5s ease-in';
        setTimeout(() => notification.remove(), 500);
    }, 5000);
}

function mostrarResultados(data) {
    // Preencher informações
    document.getElementById('resultSupermarket').textContent = formatarNomeSupermercado(data.supermercado);
    document.getElementById('resultTotal').textContent = data.total_produtos;

    const dataCompra = data.data_compra
        ? new Date(data.data_compra).toLocaleDateString('pt-BR')
        : 'Não identificada';
    document.getElementById('resultDate').textContent = dataCompra;

    const totalNota = data.total_nota || data.soma_produtos;
    document.getElementById('resultValue').textContent = totalNota.toFixed(2);

    // Preencher lista de produtos
    const productList = document.getElementById('productList');
    productList.innerHTML = '';

    data.produtos_salvos.forEach(produto => {
        const item = document.createElement('div');
        item.className = 'product-item';

        item.innerHTML = `
            <div class="product-name">
                ${produto.nome}
                ${produto.quantidade > 1 ? `<small>(${produto.quantidade}x)</small>` : ''}
            </div>
            <div class="product-price">R$ ${produto.preco.toFixed(2)}</div>
        `;

        productList.appendChild(item);
    });

    // Mostrar tokens ganhos (se houver)
    if (data.tokens_ganhos && data.tokens_ganhos > 0) {
        document.getElementById('tokensAmount').textContent = data.tokens_ganhos;
        document.getElementById('tokensEarned').style.display = 'block';

        // Atualizar carteira se a função existir
        if (window.opener && window.opener.atualizarCarteira) {
            window.opener.atualizarCarteira();
        }
    }

    // Mostrar seção de resultados
    resultSection.classList.add('show');

    // Scroll para resultados
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

function formatarNomeSupermercado(slug) {
    const names = {
        'carrefour': 'Carrefour',
        'pao_acucar': 'Pão de Açúcar',
        'extra': 'Extra',
        'atacadao': 'Atacadão',
        'dia': 'Dia%',
        'assai': 'Assaí',
        'walmart': 'Walmart',
        'big': 'Big',
        'mambo': 'Mambo'
    };
    return names[slug] || slug;
}

async function debugOCR() {
    // Criar FormData
    const formData = new FormData();
    formData.append('file', selectedFile);

    // Mostrar loading
    loading.classList.add('show');
    if (debugBtn) debugBtn.disabled = true;
    if (scanBtn) scanBtn.disabled = true;
    errorMessage.classList.remove('show');

    try {
        const response = await fetch(`${API_URL}/api/debug-ocr`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        // Criar modal para mostrar debug
        const modal = document.createElement('div');
        modal.id = 'debugModal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            z-index: 9999;
            overflow: auto;
            padding: 20px;
        `;

        // Função para fechar o modal
        const fecharModal = () => {
            modal.remove();
        };

        modal.innerHTML = `
            <div style="background: white; max-width: 800px; margin: 0 auto; border-radius: 12px; padding: 30px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h2>🔍 Debug OCR</h2>
                    <button id="btnFecharDebug" style="background: #f44336; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer;">Fechar</button>
                </div>

                <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <h3>📊 Resumo:</h3>
                    <p><strong>Supermercado:</strong> ${data.supermercado_identificado || '❌ Não identificado'}</p>
                    <p><strong>Data:</strong> ${data.data_identificada ? new Date(data.data_identificada).toLocaleDateString('pt-BR') : '❌ Não identificada'}</p>
                    <p><strong>Produtos encontrados:</strong> ${data.produtos_encontrados}</p>
                    <p><strong>Total:</strong> R$ ${data.total_encontrado ? data.total_encontrado.toFixed(2) : '❌ Não encontrado'}</p>
                    <p><strong>Total de linhas:</strong> ${data.total_linhas}</p>
                </div>

                <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <h3>📦 Primeiros produtos encontrados:</h3>
                    ${data.produtos.map(p => `
                        <div style="background: white; padding: 10px; margin: 5px 0; border-radius: 6px;">
                            <strong>${p.nome}</strong> - R$ ${p.preco.toFixed(2)} (${p.quantidade}x)
                        </div>
                    `).join('')}
                </div>

                <div style="background: #fff3e0; padding: 15px; border-radius: 8px;">
                    <h3>📝 Primeiras 30 linhas extraídas:</h3>
                    <pre style="background: white; padding: 15px; border-radius: 6px; overflow-x: auto; font-size: 12px; max-height: 400px; overflow-y: auto;">${data.primeiras_30_linhas.join('\n')}</pre>
                </div>

                <div style="background: #f1f1f1; padding: 15px; border-radius: 8px; margin-top: 20px;">
                    <h3>💡 Dicas para melhorar:</h3>
                    <ul style="margin: 10px 0;">
                        <li>Se o supermercado não foi identificado, verifique se o nome aparece nas primeiras linhas</li>
                        <li>Se a data não foi encontrada, procure por padrões como DD/MM/YYYY no texto</li>
                        <li>Se poucos produtos foram encontrados, a foto pode estar com baixa qualidade</li>
                        <li>Tente tirar uma foto mais nítida e com boa iluminação</li>
                    </ul>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Adicionar evento ao botão fechar depois de adicionar ao DOM
        setTimeout(() => {
            const btnFechar = document.getElementById('btnFecharDebug');
            if (btnFechar) {
                btnFechar.onclick = fecharModal;
            }
        }, 100);

    } catch (error) {
        console.error('Erro:', error);
        showError('Erro ao fazer debug. Verifique se o servidor está rodando.');
    } finally {
        loading.classList.remove('show');
        if (debugBtn) debugBtn.disabled = false;
        if (scanBtn) scanBtn.disabled = false;
    }
}

function showError(message) {
    if (errorMessage) {
        errorMessage.textContent = message;
        errorMessage.classList.add('show');
    }
    if (scanBtn) scanBtn.disabled = false;
    if (debugBtn) debugBtn.disabled = false;

    setTimeout(() => {
        if (errorMessage) errorMessage.classList.remove('show');
    }, 5000);
}

function escanearOutraNota() {
    // Limpar tudo
    selectedFile = null;
    previewSection.style.display = 'none';
    resultSection.classList.remove('show');
    if (scanBtn) scanBtn.disabled = true;
    if (debugBtn) debugBtn.disabled = true;
    errorMessage.classList.remove('show');
    fileInput.value = ''; // Limpar input

    // Scroll para o topo
    window.scrollTo({ top: 0, behavior: 'smooth' });

    console.log('Pronto para escanear outra nota');
}
