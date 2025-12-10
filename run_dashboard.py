"""
Script para Executar Dashboard do IntegaGal
Fase 3.1
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from interface.dashboard import Dashboard

if __name__ == '__main__':
    print("=" * 60)
    print("🧬 IntegaGal - Dashboard de Análises")
    print("=" * 60)
    print("\nIniciando interface gráfica...")
    print("Pressione Ctrl+C para sair\n")
    
    try:
        app = Dashboard()
        app.mainloop()
    except KeyboardInterrupt:
        print("\n\nEncerrando aplicação...")
    except Exception as e:
        print(f"\n❌ Erro ao executar dashboard: {e}")
        import traceback
        traceback.print_exc()
