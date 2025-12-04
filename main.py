"""
Ponto de entrada principal da aplicação IntegraGAL v2.0 - VERSÃO REFATORADA
Usando arquitetura modular com gerenciadores separados para melhor manutenibilidade.
"""

import os

# Garante BASE_DIR no sys.path
from services.system_paths import BASE_DIR
# Importações dos novos módulos refatorados
from ui.main_window import criar_aplicacao_principal
from utils.logger import registrar_log


# Para compatibilidade - manter funções utilitárias globais
def _formatar_para_gal(df):
    """Formatar dados para exportação GAL (função utilitária mantida para compatibilidade)"""
    df_out = df.copy()
    for c in ["Unnamed: 0", "index"]:
        if c in df_out.columns:
            df_out.drop(columns=[c], inplace=True)

    def _norm(col):
        import unicodedata

        col2 = str(col).strip()
        col2 = (
            unicodedata.normalize("NFKD", col2)
            .encode("ASCII", "ignore")
            .decode("ASCII")
        )
        return col2.replace(" ", "_").lower()

    df_out.columns = [_norm(c) for c in df_out.columns]

    cols = list(df_out.columns)
    orden = []
    for c in ["poco", "well", "amostra", "codigo"]:
        if c in cols and c not in orden:
            orden.append(c)
    resultado_cols = [c for c in cols if c.startswith("resultado_")]
    orden.extend([c for c in resultado_cols if c not in orden])
    for t in ["sc2", "hmpv", "inf_a", "inf_b", "adv", "rsv", "hrv"]:
        if t in cols and t not in orden:
            orden.append(t)
    for c in ["rp_1", "rp_2", "rp1", "rp2"]:
        if c in cols and c not in orden:
            orden.append(c)
    for c in cols:
        if c not in orden:
            orden.append(c)
    try:
        df_out = df_out[orden]
    except Exception:
        pass
    return df_out


def _notificar_gal_saved(path, parent=None, timeout=5000):
    """Notificar salvamento GAL (função utilitária mantida para compatibilidade)"""
    try:
        import customtkinter as ctk

        msg = f"GAL salvo: {os.path.basename(path)}\n{path}"
        if parent is None:
            registrar_log("Export GAL", msg, "INFO")
            return
        notif = ctk.CTkToplevel(parent)
        notif.overrideredirect(True)
        notif.attributes("-topmost", True)
        lbl = ctk.CTkLabel(
            notif, text=msg, fg_color="#222", text_color="white", corner_radius=8
        )
        lbl.pack(padx=10, pady=(8, 6))
        btn_frame = ctk.CTkFrame(notif)
        btn_frame.pack(padx=8, pady=(0, 8))

        def _open_path(p):
            try:
                if os.name == "nt":
                    os.startfile(p)
                else:
                    import subprocess

                    subprocess.Popen(["xdg-open" if os.name == "posix" else "open", p])
            except Exception:
                registrar_log("Export GAL", f"Falha ao abrir caminho {p}", "WARNING")

        try:
            folder = os.path.dirname(path)
            ctk.CTkButton(
                btn_frame,
                text="Abrir pasta",
                width=120,
                command=lambda: _open_path(folder),
            ).pack(side="left", padx=6)
            ctk.CTkButton(
                btn_frame,
                text="Abrir arquivo",
                width=120,
                command=lambda: _open_path(path),
            ).pack(side="left", padx=6)
        except Exception:
            pass
        try:
            x = parent.winfo_rootx() + 50
            y = parent.winfo_rooty() + 50
            notif.geometry(f"+{x}+{y}")
        except Exception:
            pass
        notif.after(timeout, notif.destroy)
        registrar_log(
            "Export GAL", f"Notificação exibida para arquivo GAL: {path}", "INFO"
        )
    except Exception:
        pass


if __name__ == "__main__":
    """Ponto de entrada principal da aplicação"""
    os.chdir(BASE_DIR)

    app = criar_aplicacao_principal()
    if app:
        app.mainloop()
