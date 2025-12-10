"""
Script para testar Gráficos de Qualidade
"""

import customtkinter as ctk
from interface.graficos_qualidade import GraficosQualidade


def main():
    """Testa gráficos de qualidade com dados de exemplo"""
    print("Abrindo Gráficos de Qualidade...")
    
    app = ctk.CTk()
    app.withdraw()  # Esconder janela principal
    
    # Abrir gráficos (com dados de exemplo gerados automaticamente)
    graficos = GraficosQualidade(app)
    
    print("Gráficos abertos. Feche a janela para encerrar.")
    
    app.mainloop()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Erro ao executar gráficos: {e}")
        import traceback
        traceback.print_exc()
