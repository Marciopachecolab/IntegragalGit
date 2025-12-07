import pandas as pd
import customtkinter as ctk
from services.plate_viewer import PlateModel, PlateWindow

records = [
    {"Poco": "A01", "Amostra": "S_RP_OK", "Codigo": "C1", "RP": 36.5, "Resultado_INFA": "ND", "INFA": ""},
]

df = pd.DataFrame(records)

# Construir modelo e abrir janela ligada a um root que executa mainloop()
plate_model = PlateModel.from_df(df, exame="vr1e2_biomanguinhos_7500")
root = ctk.CTk()
win = PlateWindow(root, plate_model, {"exame": "vr1e2_biomanguinhos_7500", "usuario": "tester"})
root.mainloop()
