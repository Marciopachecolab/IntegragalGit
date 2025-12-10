"""
Teste de visualização do Mapa de Placa com valores vazios/NaN
para avaliação da distribuição dos elementos na interface.
"""

import customtkinter as ctk
import pandas as pd
import numpy as np

# Importar o módulo plate_viewer
# Ajuste o caminho conforme necessário
from services.plate_viewer import PlateModel, PlateWindow, abrir_placa_ctk

# Configurar aparência
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


def criar_df_vazio_96_pocos() -> pd.DataFrame:
    """
    Cria um DataFrame com 96 poços, todos com valores NaN/vazios.
    Simula uma placa completa sem dados para visualização do layout.
    """
    rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    cols = range(1, 13)
    
    registros = []
    for row in rows:
        for col in cols:
            poco = f"{row}{col:02d}"
            registros. append({
                "Poco": poco,
                "Amostra": np.nan,
                "Codigo": np.nan,
                "Resultado_SC2": np.nan,
                "Resultado_HMPV": np.nan,
                "Resultado_INFA": np.nan,
                "Resultado_INFB": np.nan,
                "Resultado_ADV": np.nan,
                "Resultado_RSV": np.nan,
                "Resultado_HRV": np.nan,
                "SC2": np.nan,
                "HMPV": np. nan,
                "INFA": np.nan,
                "INFB": np.nan,
                "ADV": np. nan,
                "RSV": np.nan,
                "HRV": np.nan,
                "RP_1": np.nan,
                "RP_2": np.nan,
            })
    
    return pd.DataFrame(registros)


def criar_df_vazio_48_testes() -> pd.DataFrame:
    """
    Cria um DataFrame com 48 testes (pares de poços), todos com valores NaN/vazios.
    Simula uma placa de 48 testes para visualização do layout com grupos.
    """
    rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    cols = range(1, 13, 2)  # 1, 3, 5, 7, 9, 11
    
    registros = []
    for row in rows:
        for col in cols:
            poco1 = f"{row}{col:02d}"
            poco2 = f"{row}{col+1:02d}"
            poco_combinado = f"{poco1}+{poco2}"
            
            registros.append({
                "Poco": poco_combinado,
                "Amostra": np.nan,
                "Codigo": np.nan,
                "Resultado_SC2": np. nan,
                "Resultado_HMPV": np.nan,
                "Resultado_INFA": np.nan,
                "Resultado_INFB": np.nan,
                "SC2": np.nan,
                "HMPV": np. nan,
                "INFA": np.nan,
                "INFB": np.nan,
                "RP_1": np.nan,
                "RP_2": np.nan,
            })
    
    return pd.DataFrame(registros)


def criar_df_vazio_32_testes() -> pd.DataFrame:
    """
    Cria um DataFrame com 32 testes (trios de poços), todos com valores NaN/vazios.
    Simula uma placa de 32 testes para visualização do layout com grupos de 3.
    """
    rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    cols = range(1, 13, 3)  # 1, 4, 7, 10
    
    registros = []
    for row in rows:
        for col in cols:
            poco1 = f"{row}{col:02d}"
            poco2 = f"{row}{col+1:02d}"
            poco3 = f"{row}{col+2:02d}"
            poco_combinado = f"{poco1}+{poco2}+{poco3}"
            
            registros.append({
                "Poco": poco_combinado,
                "Amostra": np.nan,
                "Codigo": np.nan,
                "Resultado_SC2": np. nan,
                "Resultado_HMPV": np.nan,
                "SC2": np.nan,
                "HMPV": np. nan,
                "RP_1": np.nan,
            })
    
    return pd. DataFrame(registros)


def criar_df_vazio_24_testes() -> pd.DataFrame:
    """
    Cria um DataFrame com 24 testes (quartetos de poços), todos com valores NaN/vazios.
    Simula uma placa de 24 testes para visualização do layout com grupos de 4. 
    """
    rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    cols = range(1, 13, 4)  # 1, 5, 9
    
    registros = []
    for row in rows:
        for col in cols:
            poco1 = f"{row}{col:02d}"
            poco2 = f"{row}{col+1:02d}"
            poco3 = f"{row}{col+2:02d}"
            poco4 = f"{row}{col+3:02d}"
            poco_combinado = f"{poco1}+{poco2}+{poco3}+{poco4}"
            
            registros.append({
                "Poco": poco_combinado,
                "Amostra": np. nan,
                "Codigo": np.nan,
                "Resultado_SC2": np.nan,
                "SC2": np.nan,
                "RP_1": np.nan,
            })
    
    return pd.DataFrame(registros)


def main():
    """
    Função principal para testar a visualização da placa.
    Descomente a opção desejada para testar diferentes layouts.
    """
    
    # ============================================================
    # ESCOLHA O TIPO DE PLACA PARA TESTAR (descomente uma opção)
    # ============================================================
    
    # Opção 1: Placa de 96 poços individuais
    df_teste = criar_df_vazio_96_pocos()
    tipo_placa = "96 poços individuais"
    
    # Opção 2: Placa de 48 testes (pares)
    # df_teste = criar_df_vazio_48_testes()
    # tipo_placa = "48 testes (pares)"
    
    # Opção 3: Placa de 32 testes (trios)
    # df_teste = criar_df_vazio_32_testes()
    # tipo_placa = "32 testes (trios)"
    
    # Opção 4: Placa de 24 testes (quartetos)
    # df_teste = criar_df_vazio_24_testes()
    # tipo_placa = "24 testes (quartetos)"
    
    # ============================================================
    
    print(f"\n{'='*60}")
    print(f"TESTE DE VISUALIZAÇÃO - MAPA DE PLACA VAZIO")
    print(f"{'='*60}")
    print(f"Tipo de placa: {tipo_placa}")
    print(f"Total de registros no DataFrame: {len(df_teste)}")
    print(f"Colunas: {list(df_teste.columns)}")
    print(f"{'='*60}\n")
    
    # Metadados de exemplo
    meta = {
        "data": "08/12/2025",
        "extracao": "TESTE_LAYOUT",
        "exame": "Teste Visualização",
        "usuario": "Desenvolvedor",
        "arquivo": "teste_vazio.csv"
    }
    
    # Criar janela principal CTk
    root = ctk.CTk()
    root.withdraw()  # Esconder janela principal
    
    # Abrir visualizador da placa
    print("Abrindo visualizador da placa...")
    win = abrir_placa_ctk(df_teste, meta_extra=meta, parent=root)
    
    if win:
        print("Janela aberta com sucesso!")
        print("\nInstruções:")
        print("- Clique em qualquer poço para ver os detalhes no painel lateral")
        print("- Observe a distribuição e tamanho dos elementos")
        print("- Feche a janela para encerrar o teste")
        
        # Manter a aplicação rodando
        root.mainloop()
    else:
        print("ERRO: Não foi possível abrir a janela do visualizador.")
        root.destroy()


if __name__ == "__main__":
    main()