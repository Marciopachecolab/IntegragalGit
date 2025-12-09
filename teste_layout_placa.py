"""
Teste rápido de layout da placa - versão direta
Salve como: teste_layout_rapido.py
"""

import sys
sys.path.insert(0, '.')

import customtkinter as ctk
import pandas as pd
import numpy as np

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ============================================================
# CONFIGURAÇÃO: Altere aqui o tipo de placa desejado
# ============================================================
TIPO_PLACA = 96  # Opções: 96, 48, 32, 24
# ============================================================

def criar_df_vazio(tipo: int) -> pd.DataFrame:
    """Cria DataFrame vazio baseado no tipo de placa."""
    rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    registros = []
    
    if tipo == 96:
        step = 1
        group_size = 1
    elif tipo == 48:
        step = 2
        group_size = 2
    elif tipo == 32:
        step = 3
        group_size = 3
    elif tipo == 24:
        step = 4
        group_size = 4
    else:
        step = 1
        group_size = 1
    
    for row in rows:
        for col in range(1, 13, step):
            if group_size == 1:
                poco = f"{row}{col:02d}"
            else:
                pocos = [f"{row}{col+i:02d}" for i in range(group_size) if col+i <= 12]
                poco = "+".join(pocos)
            
            registros.append({
                "Poco": poco,
                "Amostra": "",
                "Codigo": "",
                "Resultado_SC2": "",
                "Resultado_HMPV": "",
                "SC2": np.nan,
                "HMPV": np. nan,
                "RP_1": np.nan,
            })
    
    return pd. DataFrame(registros)


if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"TESTE DE LAYOUT - PLACA DE {TIPO_PLACA} TESTES")
    print(f"{'='*60}\n")
    
    df = criar_df_vazio(TIPO_PLACA)
    print(f"DataFrame criado: {len(df)} registros")
    
    meta = {
        "data": "08/12/2025",
        "extracao": "TESTE_LAYOUT",
        "exame": f"Layout {TIPO_PLACA}",
        "usuario": "Dev",
    }
    
    from services.plate_viewer import abrir_placa_ctk
    
    root = ctk.CTk()
    root.withdraw()
    
    win = abrir_placa_ctk(df, meta_extra=meta, parent=root)
    
    if win:
        print("Janela aberta!  Feche para encerrar.")
        root.mainloop()