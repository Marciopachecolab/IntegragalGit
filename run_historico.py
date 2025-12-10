"""
Script para testar Histórico de Análises
"""

import customtkinter as ctk
from interface.historico_analises import HistoricoAnalises


def main():
    """Testa histórico com dados de exemplo"""
    print("Abrindo Histórico de Análises...")
    
    app = ctk.CTk()
    app.withdraw()  # Esconder janela principal
    
    # Abrir histórico (com dados de exemplo gerados automaticamente)
    historico = HistoricoAnalises(app)
    
    print("Histórico aberto. Feche a janela para encerrar.")
    
    app.mainloop()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Erro ao executar histórico: {e}")
        import traceback
        traceback.print_exc()
