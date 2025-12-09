"""
Versão standalone para teste rápido do layout da placa.
"""

import customtkinter as ctk
import pandas as pd
import numpy as np
import sys
sys.path.insert(0, '.')  # Adicionar diretório atual ao path

# Configurar aparência
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

def main():
    # Criar DataFrame vazio com 96 poços
    rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    registros = []
    
    for row in rows:
        for col in range(1, 13):
            registros.append({
                "Poco": f"{row}{col:02d}",
                "Amostra": "",
                "Codigo": "",
                "Resultado_SC2": "",
                "SC2": np.nan,
                "RP_1": np.nan,
            })
    
    df_teste = pd.DataFrame(registros)
    
    meta = {
        "data": "08/12/2025",
        "extracao": "TESTE",
        "exame": "Layout Test",
        "usuario": "Dev",
    }
    
    # Importar e abrir
    from services.plate_viewer import abrir_placa_ctk
    
    root = ctk.CTk()
    root.withdraw()
    
    win = abrir_placa_ctk(df_teste, meta_extra=meta, parent=root)
    
    if win:
        root.mainloop()

if __name__ == "__main__":
    main()