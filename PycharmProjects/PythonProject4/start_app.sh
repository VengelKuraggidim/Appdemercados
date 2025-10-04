#!/bin/bash
# Script para iniciar o Comparador de Preços

echo "🚀 Iniciando Comparador de Preços..."
echo "===================================="

# Mata processos existentes nas portas
echo "🔄 Parando servidores anteriores..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8080 | xargs kill -9 2>/dev/null
sleep 1

# Inicia o backend (API) - COM RELOAD e servindo frontend
echo "🔧 Iniciando API Backend (porta 8000)..."
echo "📍 Incluindo análise de geolocalização e custo-benefício!"
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload > /dev/null 2>&1 &
BACKEND_PID=$!
sleep 3

# Verifica se o backend iniciou (com retry)
for i in {1..5}; do
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        echo "✅ Backend rodando em http://localhost:8000"
        break
    fi
    if [ $i -eq 5 ]; then
        echo "❌ Erro ao iniciar backend"
        exit 1
    fi
    sleep 1
done

# Inicia o frontend
echo "🌐 Iniciando Frontend (porta 8080)..."
cd frontend && python -m http.server 8080 > /dev/null 2>&1 &
FRONTEND_PID=$!
cd ..
sleep 1

# Verifica se o frontend iniciou
if curl -s http://localhost:8080 > /dev/null; then
    echo "✅ Frontend rodando em http://localhost:8080"
else
    echo "❌ Erro ao iniciar frontend"
    exit 1
fi

echo ""
echo "===================================="
echo "✅ App iniciado com sucesso!"
echo "===================================="
echo ""
echo "📱 Acesse o app em:"
echo "   🌐 http://localhost:8000 (servido pelo FastAPI)"
echo "   🌐 http://localhost:8080 (servidor alternativo)"
echo ""
echo "📊 API disponível em:"
echo "   🔧 http://localhost:8000/api"
echo ""
echo "💾 Banco de dados: precos.db"
echo ""
echo "Para parar o app, execute:"
echo "   ./stop_app.sh"
echo "   ou pressione Ctrl+C"
echo ""
echo "===================================="

# Mantém o script rodando
trap "echo ''; echo '🛑 Parando servidores...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ App parado'; exit 0" INT TERM

# Aguarda
wait
