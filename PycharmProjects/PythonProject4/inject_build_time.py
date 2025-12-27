#!/usr/bin/env python3
"""
Script para injetar timestamp de build no Service Worker
Executa automaticamente antes de iniciar o servidor
"""
import os
import time
from pathlib import Path

def inject_build_time():
    """Substitui __BUILD_TIME__ no sw.js com timestamp atual"""
    sw_path = Path(__file__).parent / 'frontend' / 'sw.js'

    if not sw_path.exists():
        print(f"⚠️  Service Worker não encontrado em {sw_path}")
        return

    # Lê o conteúdo
    content = sw_path.read_text(encoding='utf-8')

    # Gera timestamp único
    build_time = str(int(time.time() * 1000))

    # Substitui o placeholder
    updated_content = content.replace('__BUILD_TIME__', build_time)

    # Escreve de volta
    sw_path.write_text(updated_content, encoding='utf-8')

    print(f"✅ Service Worker atualizado com build time: {build_time}")
    print(f"   Cache name: comparador-precos-{build_time}")

if __name__ == '__main__':
    inject_build_time()
