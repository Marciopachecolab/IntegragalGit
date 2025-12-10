"""
Ponto de entrada principal da aplicação IntegraGAL v2.0 - versão refatorada.
Mantém utilitários globais (_formatar_para_gal) para compatibilidade.
"""

import os
from datetime import datetime

from services.system_paths import BASE_DIR
from ui.main_window import criar_aplicacao_principal
from utils.logger import registrar_log


# Backward compatibility - redireciona para módulos específicos
def _formatar_para_gal(df, exam_cfg=None, exame: str | None = None):
    """
    DEPRECATED: Use exportacao.gal_formatter.formatar_para_gal() diretamente.
    Mantido apenas para compatibilidade com código legado.
    """
    from exportacao.gal_formatter import formatar_para_gal
    return formatar_para_gal(df, exam_cfg=exam_cfg, exame=exame)


def _formatar_para_gal_OLD(df, exam_cfg=None, exame: str | None = None):
    """Formata o resultado para layout GAL usando metadados do exame (registry)."""
    import unicodedata
    import pandas as pd
    from services.exam_registry import get_exam_cfg

    cfg = exam_cfg or (get_exam_cfg(exame) if exame else get_exam_cfg(""))

    df_in = df.copy()
    for c in ["Unnamed: 0", "index"]:
        if c in df_in.columns:
            df_in = df_in.drop(columns=[c])

    def _strip_accents(txt: str) -> str:
        return (
            unicodedata.normalize("NFKD", txt)
            .encode("ASCII", "ignore")
            .decode("ASCII")
        )

    def _norm(col: str) -> str:
        col2 = str(col).strip()
        col2 = _strip_accents(col2)
        return col2.replace(" ", "_").lower()

    colmap = {_norm(c): c for c in df_in.columns}

    def _get(col_names, default=""):
        for name in col_names:
            key = _norm(name)
            if key in colmap:
                return df_in[colmap[key]]
        return pd.Series([default] * len(df_in))

    def _map_result(val):
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return ""
        s = str(val).strip().lower()
        if "inconcl" in s:
            return "3"
        if "nao" in s and "detect" in s:
            return "2"
        if "detect" in s:
            return "1"
        return ""

    df_out = pd.DataFrame()
    cod_col = _get(["codigo", "amostra"])
    df_out["codigoAmostra"] = cod_col
    df_out["codigo"] = cod_col
    df_out["requisicao"] = ""
    df_out["paciente"] = ""
    df_out["exame"] = cfg.nome_exame or "VRSRT"
    df_out["metodo"] = "RTTR"
    df_out["registroInterno"] = cod_col
    df_out["kit"] = str(cfg.kit_codigo or "427")
    df_out["reteste"] = ""
    df_out["loteKit"] = ""
    df_out["dataProcessamentoFim"] = datetime.now().strftime("%d/%m/%Y")
    df_out["valorReferencia"] = ""
    df_out["observacao"] = ""
    df_out["painel"] = cfg.panel_tests_id or "1"
    df_out["resultado"] = ""

    export_fields = cfg.export_fields or []
    if not export_fields:
        export_fields = [
            "Influenzaa",
            "influenzab",
            "coronavirusncov",
            "adenovirus",
            "vsincicialresp",
            "metapneumovirus",
            "rinovirus",
        ]

    def _find_result_col(target_norm: str):
        """
        Procura coluna de resultado compatível com o analito exportado,
        usando alias para mapear nomes de painel (influenzaa, adenovirus, etc.)
        para os alvos internos (INF A, ADV, ...).
        """
        # aliases básicos painel -> alvo interno
        aliases = {
            "INFLUENZAA": "INF A",
            "INFLUENZAB": "INF B",
            "ADENOVIRUS": "ADV",
            "ADENOVÍRUS": "ADV",
            "METAPNEUMOVIRUS": "HMPV",
            "RINOVIRUS": "HRV",
            "RINOVÍRUS": "HRV",
            "SARS-COV-2": "SC2",
            "SARSCOV2": "SC2",
            "CORONAVIRUSNCOV": "SC2",
        }
        # normaliza alvo exportado
        tnorm_raw = _strip_accents(target_norm).upper().replace("_", " ").replace("-", " ").strip()
        if tnorm_raw in aliases:
            tnorm_raw = aliases[tnorm_raw]
        # aplica normalize_target do exame (mapeia INFA -> INF A, etc.)
        tnorm = cfg.normalize_target(tnorm_raw).upper()

        def _clean(s: str) -> str:
            return (
                _strip_accents(s)
                .upper()
                .replace("RESULTADO", "")
                .replace("_", "")
                .replace(" ", "")
            )

        # tenta bater com colunas existentes
        for k, v in colmap.items():
            if _clean(k) == _clean(tnorm):
                return v
        # tenta prefácio Resultado_<alvo>
        cand = f"Resultado_{tnorm}"
        for k, v in colmap.items():
            if _clean(k) == _clean(cand):
                return v
        return None

    def _exportavel(code: str) -> bool:
        if not code:
            return False
        c = code.upper()
        # Usa lista de controles definida no exam_cfg quando disponível
        try:
            controles = cfg.controles or {"cn": [], "cp": []}
            cn_list = [str(x).upper() for x in (controles.get("cn") or [])]
            cp_list = [str(x).upper() for x in (controles.get("cp") or [])]
            # comparar igualdade ou substring para cobrir variações como 'CN', 'CONTROLE N'
            for v in cn_list:
                if v and v in c:
                    return False
            for v in cp_list:
                if v and v in c:
                    return False
        except Exception:
            # fallback para checagem simples
            if "CN" in c or "CP" in c:
                return False
        # somente códigos numéricos são exportáveis
        return c.isdigit()

    export_mask = cod_col.apply(_exportavel)
    df_out = df_out.loc[export_mask].reset_index(drop=True)
    df_in = df_in.loc[export_mask].reset_index(drop=True)

    for analito in export_fields:
        alvo_norm = cfg.normalize_target(analito)
        res_col = _find_result_col(alvo_norm)
        if res_col and res_col in df_in.columns:
            serie_res = df_in[res_col].apply(_map_result)
        else:
            serie_res = pd.Series([""] * len(df_in))
        col_nome = _strip_accents(analito).replace(" ", "").replace("-", "").replace("_", "").lower()
        df_out[col_nome] = serie_res

    return df_out


def gerar_painel_csvs(df_resultados, exam_cfg=None, exame: str | None = None, output_dir: str | None = None):
    """
    DEPRECATED: Use exportacao.gal_formatter.gerar_painel_csvs() diretamente.
    Mantido apenas para compatibilidade com código legado.
    """
    from exportacao.gal_formatter import gerar_painel_csvs as gerar_painel_csvs_impl
    return gerar_painel_csvs_impl(df_resultados, exam_cfg=exam_cfg, exame=exame, output_dir=output_dir)


def _notificar_gal_saved(path, parent=None, timeout=5000):
    """
    DEPRECATED: Use utils.notifications.notificar_gal_saved() diretamente.
    Mantido apenas para compatibilidade com código legado.
    """
    from utils.notifications import notificar_gal_saved
    return notificar_gal_saved(path, parent=parent, timeout=timeout)


def main_cli():
    """
    Interface de linha de comando (CLI) para executar módulos específicos.
    
    Uso:
        python main.py              # Abre GUI principal (padrão)
        python main.py dashboard    # Abre Dashboard
        python main.py historico    # Abre Histórico
        python main.py alertas      # Abre Sistema de Alertas
        python main.py graficos     # Abre Gráficos
        python main.py visualizador # Abre Visualizador de Placas
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="IntegRAGal - Sistema Integrado de Análises Laboratoriais",
        epilog="Se nenhum comando for especificado, abre a interface gráfica principal."
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Subcomandos
    subparsers.add_parser('dashboard', help='Abrir Dashboard de Análises')
    subparsers.add_parser('historico', help='Abrir Visualizador de Histórico')
    subparsers.add_parser('alertas', help='Abrir Sistema de Alertas')
    subparsers.add_parser('graficos', help='Abrir Gráficos e Estatísticas')
    subparsers.add_parser('visualizador', help='Abrir Visualizador de Placas')
    
    args = parser.parse_args()
    
    if args.command == 'dashboard':
        registrar_log("Main", "Iniciando Dashboard via CLI", "INFO")
        from interface.dashboard import Dashboard
        app = Dashboard()
        app.mainloop()
        
    elif args.command == 'historico':
        registrar_log("Main", "Iniciando Histórico via CLI", "INFO")
        from interface.historico_analises import HistoricoAnalises
        # HistoricoAnalises requer um master window
        import customtkinter as ctk
        root = ctk.CTk()
        root.withdraw()  # Esconder janela principal
        app = HistoricoAnalises(root)
        app.mainloop()
        
    elif args.command == 'alertas':
        registrar_log("Main", "Iniciando Sistema de Alertas via CLI", "INFO")
        from interface.sistema_alertas import CentroNotificacoes
        app = CentroNotificacoes()
        app.mainloop()
        
    elif args.command == 'graficos':
        registrar_log("Main", "Iniciando Gráficos via CLI", "INFO")
        from interface.graficos_qualidade import GraficosQualidade
        # GraficosQualidade requer um master window
        import customtkinter as ctk
        root = ctk.CTk()
        root.withdraw()  # Esconder janela principal
        app = GraficosQualidade(root)
        app.mainloop()
        
    elif args.command == 'visualizador':
        registrar_log("Main", "Iniciando Visualizador via CLI", "INFO")
        # Executar script standalone de visualização
        import subprocess
        subprocess.run([sys.executable, "visualizar_placa_csv.py"])
        
    else:
        # Modo GUI padrão
        app = criar_aplicacao_principal()
        if app:
            app.mainloop()


if __name__ == "__main__":
    """Ponto de entrada principal da aplicação"""
    import sys
    
    os.chdir(BASE_DIR)
    
    # Se houver argumentos de linha de comando, usar CLI
    # Caso contrário, abrir GUI principal
    if len(sys.argv) > 1:
        main_cli()
    else:
        app = criar_aplicacao_principal()
        if app:
            app.mainloop()
