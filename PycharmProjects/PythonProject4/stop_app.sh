#!/bin/bash
# Script para parar o Comparador de Preços

echo "🛑 Parando Comparador de Preços..."
echo "===================================="

# Para os servidores e o agendador
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8080 | xargs kill -9 2>/dev/null
pkill -f "agendador_precos.py" 2>/dev/null

sleep 1

# Verifica se parou
if ! lsof -ti:8000 > /dev/null 2>&1 && ! lsof -ti:8080 > /dev/null 2>&1; then
    echo "✅ Servidores parados com sucesso!"
else
    echo "⚠️  Alguns processos ainda podem estar rodando"
fi

echo "✅ Agendador parado"
echo ""
echo "💾 Dados salvos em: precos.db"
echo ""
echo "Para iniciar novamente, execute:"
echo "   ./start_app.sh ou ./iniciar_com_agendador.sh"
echo ""
echo "===================================="
