#!/bin/bash

echo "🚀 Iniciando Comparador de Preços com Agendador Automático..."
echo "===================================================================="

# Parar processos anteriores
pkill -f "uvicorn app.api.main:app" 2>/dev/null
pkill -f "python.*http.server" 2>/dev/null
pkill -f "agendador_precos.py" 2>/dev/null

echo ""
echo "🔧 Iniciando API Backend (porta 8000)..."
nohup uvicorn app.api.main:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
sleep 2

echo "✅ Backend rodando em http://localhost:8000"

echo ""
echo "🌐 Iniciando Frontend (porta 8080)..."
cd frontend && nohup python3 -m http.server 8080 > ../logs/frontend.log 2>&1 & cd ..
sleep 1

echo "✅ Frontend rodando em http://localhost:8080"

echo ""
echo "⏰ Iniciando Agendador de Atualização de Preços..."
nohup python3 agendador_precos.py --executar-agora > logs/agendador.log 2>&1 &
sleep 2

echo "✅ Agendador iniciado"

echo ""
echo "===================================================================="
echo "✅ Tudo iniciado com sucesso!"
echo "===================================================================="
echo ""
echo "📱 Acesse o app em:"
echo "   🌐 http://localhost:8000 (principal)"
echo "   🌐 http://localhost:8080 (alternativo)"
echo ""
echo "📊 API: http://localhost:8000/api"
echo ""
echo "⏰ Atualizações automáticas:"
echo "   • Completa: Diariamente às 6h e 18h"
echo "   • Rápida: A cada 4 horas"
echo ""
echo "📝 Logs disponíveis em:"
echo "   • API: logs/api.log"
echo "   • Frontend: logs/frontend.log"
echo "   • Agendador: logs/agendador.log"
echo ""
echo "Para parar tudo, execute: ./stop_app.sh"
echo "===================================================================="
