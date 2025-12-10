"""
Script para Executar Dashboard do IntegaGal
Fase 3.1

⚠️ DEPRECATED: Este script será removido em versões futuras.
Use: python main.py dashboard
"""

import sys
from pathlib import Path
import warnings

warnings.warn(
    "run_dashboard.py está deprecated. Use 'python main.py dashboard' em vez disso.",
    DeprecationWarning,
    stacklevel=2
)

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from interface.dashboard import Dashboard

if __name__ == '__main__':
    print("=" * 60)
    print("🧬 IntegaGal - Dashboard de Análises")
    print("⚠️  DEPRECATED: Use 'python main.py dashboard'")
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
