"""
Script para testar o Visualizador de Exame
"""

import customtkinter as ctk
from interface.visualizador_exame import VisualizadorExame, criar_dados_exame_exemplo


def main():
    """Testa visualizador com dados de exemplo"""
    print("Abrindo Visualizador de Exame...")
    
    app = ctk.CTk()
    app.withdraw()  # Esconder janela principal
    
    # Criar dados de exemplo
    dados = criar_dados_exame_exemplo()
    
    # Abrir visualizador
    visualizador = VisualizadorExame(app, dados)
    
    print("Visualizador aberto. Feche a janela para encerrar.")
    
    app.mainloop()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Erro ao executar visualizador: {e}")
        import traceback
        traceback.print_exc()
