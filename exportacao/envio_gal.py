"""
MÓDULO DE ENVIO GAL - Automação de Envio de Resultados
======================================================================

RESPONSABILIDADES:
------------------
✅ Automação de envio de resultados para sistema GAL via Selenium
✅ Gerenciamento de sessão e autenticação no GAL
✅ Preenchimento de formulários de resultados
✅ Validação e retry de envios
✅ Interface gráfica para seleção e envio de amostras

ARQUITETURA:
-----------
- Usa: exportacao/gal_formatter.py para formatar dados
- Depende de: browser/global_browser.py para gerenciar navegador
- Configuração: services/config_service.py (credenciais e endpoints)

FLUXO DE ENVIO:
--------------
1. Carregar resultados formatados (via gal_formatter)
2. Autenticar no sistema GAL
3. Navegar para formulário de entrada
4. Preencher campos com resultados
5. Submeter e validar resposta
6. Registrar histórico de envio

Ver: ANALISE_TECNICA_FUNCIONAMENTO.md (Seção 4 - Exportação GAL)
"""

# exportacao/envio_gal.py
import os
import sys
import threading
import time
from datetime import datetime
from functools import wraps
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog
from typing import Any, Dict, List, Optional, Set, Tuple

import customtkinter as ctk
import pandas as pd
import simplejson as json
from services.config_service import config_service
from services.exam_registry import get_exam_cfg
from utils.io_utils import read_data_with_auto_detection
from utils.logger import registrar_log

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumrequests import Firefox

# --- Configuração de Paths e Imports ---
# Garante que o diretório raiz do projeto (onde ficam os pacotes `services`, `utils`, etc.)
# esteja no sys.path, mesmo quando este módulo é executado diretamente.
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Linha comentada devido a alerta do ruff (E402): import em nível de módulo não posicionado no topo do arquivo.
# from services.config_service import config_service
# Linha comentada devido a alerta do ruff (E402): import em nível de módulo não posicionado no topo do arquivo.
# from services.system_paths import BASE_DIR
# Linha comentada devido a alerta do ruff (E402): import em nível de módulo não posicionado no topo do arquivo.
# from utils.io_utils import read_data_with_auto_detection
# Linha comentada devido a alerta do ruff (E402): import em nível de módulo não posicionado no topo do arquivo.
# from utils.logger import registrar_log

# --- Configurações Carregadas do Serviço Centralizado ---
GAL_CONFIG = config_service.get_gal_config()
PATHS_CONFIG = config_service.get_paths()

# --- Painéis padrão (compatíveis com scripts antigos) ---
DEFAULT_PANEL_TESTS = {
    "1": [
        "influenzaa",
        "influenzab",
        "coronavirusncov",
        "coronavirus229e",
        "coronavirusnl63",
        "coronavirushku1",
        "coronavirusoc43",
        "adenovirus",
        "vsincicialresp",
        "metapneumovirus",
        "rinovirus",
        "bocavirus",
        "enterovirus",
        "parainflu_1",
        "parainflu_2",
        "parainflu_3",
        "parainflu_4",
        "coronavirus",
        "influenzaahn",
        "metapneumovirua",
        "metapneumovirub",
        "mycoplasma",
        "parechovírus",
        "vsincicialrespa",
        "vsincicialrespb",
        "influenzaah_3",
        "influenzaah_1",
        "influenzaah_5",
        "influenzaah_7",
    ]
}


# ==============================================================================
# 1. DECORATOR DE RETENTATIVA
# ==============================================================================
def retry_with_backoff(
    retries=int(GAL_CONFIG.get("retry_settings", {}).get("max_retries", 3)),
    backoff_in_seconds=float(
        GAL_CONFIG.get("retry_settings", {}).get("backoff_factor", 1.0)
    ),
):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            attempts = 0
            last_exception = None
            while attempts < retries:
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    attempts += 1
                    sleep_time = backoff_in_seconds * (2 ** (attempts - 1))
                    log_msg = f"Tentativa {attempts}/{retries} falhou para '{f.__name__}': {e}. Aguardando {sleep_time:.2f}s."
                    if args and hasattr(args[0], "log"):
                        args[0].log(log_msg, "warning")
                    else:
                        registrar_log("Retry Decorator", log_msg, "WARNING")
                    time.sleep(sleep_time)
            raise last_exception

        return wrapper

    return decorator


# ==============================================================================
# 2. CLASSE DE SERVIÇO (LÓGICA DE NEGÓCIO DESACOPLADA DA UI)
# ==============================================================================
class GalService:
    def __init__(self, logger_callback):
        self.log = logger_callback
        self.base_url = GAL_CONFIG.get("base_url")
        self.login_ids = GAL_CONFIG.get("login_ids", {})
        self.endpoints = GAL_CONFIG.get("api_endpoints", {})
        # Une os painéis configurados com o painel padrão utilizado nos scripts antigos
        configured_panels = GAL_CONFIG.get("panel_tests", {}) or {}
        merged_panels = {}
        # Primeiro aplica os painéis configurados
        for k, v in configured_panels.items():
            merged_panels[str(k)] = list(
                dict.fromkeys(v)
            )  # remove duplicados preservando ordem
        # Em seguida garante que o painel 1 tenha todos os testes clássicos de VR
        for k, v in DEFAULT_PANEL_TESTS.items():
            if k not in merged_panels:
                merged_panels[k] = list(dict.fromkeys(v))
            else:
                merged = list(dict.fromkeys(list(merged_panels[k]) + list(v)))
                merged_panels[k] = merged
        self.panel_tests = merged_panels
        self.timeout = int(GAL_CONFIG.get("request_timeout", 30))

    @retry_with_backoff()
    def realizar_login(self, driver: WebDriver, usuario: str, senha: str):
        # Implementação exatamente como a lógica testada fornecida pelo usuário
        self.log(f"Acedendo a {self.base_url}...", "info")
        try:
            driver.get(self.base_url)

            # localizar elementos por IDs fixos (implementação conhecida e testada)
            username = driver.find_element(By.ID, "ext-comp-1008")
            password = driver.find_element(By.ID, "ext-comp-1009")
            modulo = driver.find_element(By.ID, "ext-comp-1010")
            lab = driver.find_element(By.ID, "ext-comp-1011")
            login = driver.find_element(By.ID, "ext-gen68")

            username.send_keys(usuario)
            password.send_keys(senha)
            modulo.send_keys("BIOLOGIA MEDICA")
            time.sleep(1)
            modulo.send_keys(Keys.TAB)
            time.sleep(1)
            lab.send_keys("LACEN")
            time.sleep(2)
            lab.send_keys(Keys.TAB)
            time.sleep(1)
            login.click()
            time.sleep(1)
            # navegar explicitamente para a página de laboratório conforme fluxo conhecido
            try:
                driver.get("https://galteste.saude.sc.gov.br/laboratorio/")
            except Exception:
                pass
            time.sleep(1)

            # enviar ESCAPE para fechar overlays
            try:
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            except Exception:
                pass

            time.sleep(4)
            self.log("Tentativa de login realizada (fluxo padrão).", "info")

            # confirmar login (mesma verificação usada anteriormente)
            try:
                WebDriverWait(driver, min(5, max(2, self.timeout))).until(
                    EC.presence_of_element_located((By.ID, "VERSAO-TOTAL"))
                )
                self.log("Login confirmado (VERSAO-TOTAL).", "success")
                return
            except Exception:
                try:
                    if "/laboratorio/" in driver.current_url:
                        self.log("Login presumido via URL '/laboratorio/'.", "success")
                        return
                except Exception:
                    pass

            # se chegamos aqui, trata-se de não confirmação
            # salvar debug e falhar para retrial
            try:
                debug_dir = os.path.join(BASE_DIR, "debug")
                os.makedirs(debug_dir, exist_ok=True)
                driver.save_screenshot(
                    os.path.join(debug_dir, "gal_login_unconfirmed.png")
                )
                with open(
                    os.path.join(debug_dir, "gal_login_unconfirmed.html"),
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(driver.page_source)
            except Exception:
                pass
            raise Exception("Login não confirmado após tentativa.")

        except Exception:
            # em caso de falha durante o fluxo, salvar artefatos em locais previsíveis
            try:
                debug_dirs = [
                    os.path.join(BASE_DIR, "debug"),
                    os.path.join(BASE_DIR, "exportacao", "debug"),
                ]
                for debug_dir in debug_dirs:
                    os.makedirs(debug_dir, exist_ok=True)
                    try:
                        driver.save_screenshot(
                            os.path.join(debug_dir, "gal_login_fail.png")
                        )
                    except Exception:
                        pass
                    try:
                        with open(
                            os.path.join(debug_dir, "gal_login_fail.html"),
                            "w",
                            encoding="utf-8",
                        ) as f:
                            f.write(driver.page_source)
                    except Exception:
                        pass
                    try:
                        self.log(f"Debug artifacts gravados: {debug_dir}", "info")
                    except Exception:
                        pass
            except Exception:
                pass
            raise

    @retry_with_backoff()
    def buscar_metadados(
        self, driver: WebDriver, codigos_amostra_set: Set[str]
    ) -> Dict[str, Any]:
        encontrados = {}
        url = self.base_url + self.endpoints.get("metadata")
        start, total, limit = 0, float("inf"), 500

        self.log(
            f"Iniciando busca de metadados para {len(codigos_amostra_set)} amostras.",
            "info",
        )
        while start < total and len(encontrados) < len(codigos_amostra_set):
            payload = {"limit": limit, "start": start, "dtInicio": "", "dtFim": ""}
            resp = driver.request(
                "POST",
                url,
                data=payload,
                headers={"X-Requested-With": "XMLHttpRequest"},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            total = data.get("total", 0)

            if not data.get("dados"):
                break

            for ex in data.get("dados", []):
                ca = str(ex.get("codigoAmostra", "")).strip()
                if ca in codigos_amostra_set and (
                    ca not in encontrados
                    or ex.get("codigo", 0) > encontrados[ca].get("codigo", 0)
                ):
                    encontrados[ca] = ex

            start += len(data.get("dados", []))
            self.log(
                f"Progresso da busca: {len(encontrados)}/{len(codigos_amostra_set)} encontrados.",
                "debug",
            )

        self.log(
            f"Busca de metadados finalizada: {len(encontrados)} encontrados.", "info"
        )
        return encontrados

    def construir_payload(
        self, meta: Dict, row: pd.Series, observacao_geral: str
    ) -> Dict[str, Any]:
        """
        Monta o payload exatamente no espírito dos scripts antigos:
        - Usa o painel para decidir quais testes entram em `resultados`
        - Converte valores para inteiro quando possível, caso contrário usa None
        - Respeita colunas opcionais `valorReferencia` e `observacao` do CSV, se existirem
        - Combina observação da amostra com observação geral da corrida
        """
        # Painel e lista de testes
        painel = int(row.get("painel", 1))
        testes_do_painel = self.panel_tests.get(str(painel), [])

        # Montagem de resultados
        resultados: Dict[str, Any] = {"resultado": None}
        for teste in testes_do_painel:
            # As colunas foram normalizadas para minúsculas no carregamento do CSV
            raw = row.get(teste.lower(), None)
            if pd.isna(raw) or str(raw).strip() == "":
                resultados[teste] = None
            else:
                try:
                    resultados[teste] = int(raw)
                except (ValueError, TypeError):
                    resultados[teste] = None

        # Campos de identificação / metadados
        codigo_amostra = str(row.get("codigoamostra", "")).strip()
        metodo = meta.get("metodo", "RT-PCR em tempo real")
        exame = meta.get("exame", "Vírus Respiratórios")

        # Campos opcionais vindos do CSV, se existirem, com limpeza de NaN
        valor_referencia = row.get("valorreferencia", "")
        if pd.isna(valor_referencia):
            valor_referencia = ""

        obs_csv = row.get("observacao", "")
        if pd.isna(obs_csv):
            obs_csv = ""

        # Política de observação:
        # - se a linha tiver observação, ela é priorizada
        # - a observação geral da corrida é concatenada quando ambas existem
        if obs_csv and observacao_geral:
            observacao_final = f"{str(obs_csv).strip()} | {observacao_geral}"
        elif obs_csv:
            observacao_final = str(obs_csv).strip()
        else:
            observacao_final = observacao_geral

        data_proc = row.get("dataprocessamentofim", None)
        if pd.isna(data_proc) or str(data_proc).strip() == "":
            data_proc_str = datetime.now().strftime("%d/%m/%Y")
        else:
            data_proc_str = str(data_proc)

        kit_val = row.get("kit")
        kit_int = (
            int(kit_val)
            if kit_val is not None and str(kit_val).strip().isdigit()
            else None
        )

        return {
            "codigo": str(meta.get("codigo", "")),
            "requisicao": meta.get("requisicao", ""),
            "paciente": meta.get("paciente", ""),
            "exame": exame,
            "metodo": metodo,
            "registroInterno": codigo_amostra,
            "kit": kit_int,
            "reteste": "",  # mantido vazio como nos scripts antigos
            "loteKit": str(row.get("lotekit", "")),
            "dataProcessamentoIni": "",
            "dataProcessamentoFim": data_proc_str,
            "valorReferencia": valor_referencia,
            "observacao": observacao_final,
            "painel": painel,
            "resultados": resultados,
        }

    def _validar_campo(
        self, driver: WebDriver, payload_base: Dict, campo: str, valor: Any
    ) -> Optional[str]:
        """
        Valida um único campo de `resultados`, reproduzindo a lógica dos scripts antigos:
        - Envia somente o campo em questão
        - Considera como sucesso tanto respostas com `status == "sucesso"` quanto `success == True`
        - Em caso de falha, retorna a mensagem de erro
        """
        tmp_payload = payload_base.copy()
        tmp_payload["resultados"] = {"resultado": None, campo: valor}
        url = self.base_url + self.endpoints.get("submit")

        resp = driver.request(
            "POST",
            url,
            data={"exame": json.dumps(tmp_payload, ensure_ascii=False)},
            headers={"X-Requested-With": "XMLHttpRequest"},
            timeout=self.timeout,
        )

        try:
            data = resp.json()
        except json.JSONDecodeError:
            return f"Resposta inválida do servidor (HTTP {resp.status_code})"

        ok_status = data.get("status") == "sucesso"
        ok_success = data.get("success") is True

        if resp.status_code == 200 and (ok_status or ok_success):
            return None

        motivo = (
            data.get("errorMsg")
            or data.get("message")
            or data.get("mensagem")
            or data.get("error")
            or data.get("erro")
            or f"Erro desconhecido (HTTP {resp.status_code})"
        )
        return motivo

    def _enviar_payload_completo(
        self, driver: WebDriver, payload: Dict
    ) -> Tuple[bool, Any]:
        """
        Envia o payload completo para o GAL.
        Compatível com a lógica dos scripts antigos, que verificavam `success == True`
        na resposta JSON do endpoint de gravação.
        """
        url = self.base_url + self.endpoints.get("submit")
        resp = driver.request(
            "POST",
            url,
            data={"exame": json.dumps(payload, ensure_ascii=False)},
            headers={"X-Requested-With": "XMLHttpRequest"},
            timeout=self.timeout,
        )
        # Não chamamos raise_for_status aqui para poder inspecionar a resposta mesmo em HTTP 4xx/5xx
        try:
            data = resp.json()
        except json.JSONDecodeError:
            # devolvemos também o corpo bruto para inspeção em log
            return False, {
                "message": "Resposta inválida do servidor (não é JSON)",
                "_http_status": resp.status_code,
                "_raw": resp.text[:500],
            }
        # Acrescenta metadados úteis para diagnóstico
        data.setdefault("_http_status", resp.status_code)
        # Guarda um recorte do corpo bruto para inspeção futura
        try:
            raw_text = resp.text
        except Exception:
            raw_text = ""
        if "_raw" not in data and raw_text:
            data["_raw"] = raw_text[:500]

        # Scripts antigos consideravam sucesso quando `success` era True
        success = bool(data.get("success") is True)
        return success, data

    def enviar_amostra(self, driver: WebDriver, payload: Dict) -> Dict[str, Any]:
        ca = payload.get("registroInterno")
        paciente = payload.get("paciente")
        resultado: Dict[str, Any] = {
            "codigoAmostra": ca,
            "paciente": paciente,
            "status": "",
            "erro": [],
            "campos_invalidos": [],
        }

        try:
            self.log(f"A enviar payload para {ca} (Paciente: {paciente})", "info")
            success, response = self._enviar_payload_completo(driver, payload)

            if success:
                resultado["status"] = "sucesso"
                return resultado

            # Falha no envio: tentar extrair mensagem mais informativa
            msg = (
                response.get("errorMsg")
                or response.get("message")
                or response.get("mensagem")
                or response.get("error")
                or response.get("erro")
            )
            http_status = response.get("_http_status", "desconhecido")
            if not msg:
                msg = f"Erro não especificado (HTTP {http_status})"

            resultado["status"] = "erro"
            resultado["erro"].append(msg)

            # Loga erro principal e resposta completa para diagnóstico
            self.log(
                f"Erro no envio de {ca}: {msg}. A iniciar validação de campos.", "error"
            )
            try:
                self.log(
                    f"Resposta completa do servidor para {ca}: {response}", "warning"
                )
            except Exception:
                pass

            # Validação campo a campo, como nos scripts antigos
            testes_do_painel = self.panel_tests.get(str(payload.get("painel", 1)), [])
            for teste in testes_do_painel:
                val = payload["resultados"].get(teste)
                if val is not None:
                    motivo = self._validar_campo(driver, payload, teste, val)
                    if motivo:
                        resultado["campos_invalidos"].append(
                            {
                                "campo": teste,
                                "valor": val,
                                "motivo": motivo,
                            }
                        )

            # Log detalhado dos campos inválidos, se houver
            if resultado["campos_invalidos"]:
                self.log(f"Campos inválidos identificados para {ca}:", "warning")
                for problema in resultado["campos_invalidos"]:
                    self.log(
                        f"  - {problema['campo']} = {problema['valor']}: {problema['motivo']}",
                        "warning",
                    )

            return resultado

        except Exception as e:
            resultado["status"] = "erro_critico"
            resultado["erro"].append(f"Erro inesperado no envio: {e}")
            self.log(f"Erro inesperado no envio de {ca}: {e}", "critical")
            return resultado

    def ler_csv_resultados(self, csv_path: str) -> Optional[pd.DataFrame]:
        df = read_data_with_auto_detection(csv_path)
        if df is None or df.empty:
            self.log("Arquivo CSV vazio ou ilegível.", "critical")
            return None

        df.columns = [str(col).strip().replace(" ", "").lower() for col in df.columns]
        required = ["kit", "painel", "dataprocessamentofim", "codigoamostra"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            self.log(
                f"Colunas obrigatórias em falta no CSV: {', '.join(missing)}",
                "critical",
            )
            return None

        df.dropna(subset=[c for c in required if c != "codigoamostra"], inplace=True)
        df["codigoamostra"] = (
            df["codigoamostra"]
            .astype(str)
            .str.strip()
            .str.replace(".0", "", regex=False)
        )
        df.drop(df[df["codigoamostra"] == ""].index, inplace=True)
        self.log(f"CSV lido e validado. {len(df)} registos processáveis.", "info")
        return df

    def salvar_relatorios(
        self,
        relatorio_final: List[Dict],
        relatorio_local: List[Dict],
        usuario: str,
        observacao: str,
        kit: str,
        relatorio_filename: str,
    ):
        log_dir = os.path.dirname(PATHS_CONFIG.get("log_file"))
        os.makedirs(log_dir, exist_ok=True)

        if relatorio_final:
            df_sucesso = pd.DataFrame(relatorio_final)
            # Garante coluna codigoAmostra preenchida (compatível com histórico antigo)
            if (
                "codigoAmostra" not in df_sucesso.columns
                and "registroInterno" in df_sucesso.columns
            ):
                df_sucesso["codigoAmostra"] = df_sucesso["registroInterno"]
            elif (
                "codigoAmostra" in df_sucesso.columns
                and df_sucesso["codigoAmostra"].isna().any()
                and "registroInterno" in df_sucesso.columns
            ):
                df_sucesso["codigoAmostra"] = df_sucesso["codigoAmostra"].fillna(
                    df_sucesso["registroInterno"]
                )
            caminho_historico = PATHS_CONFIG.get("gal_upload_history_csv")
            os.makedirs(os.path.dirname(caminho_historico), exist_ok=True)
            all_cols_base = [
                "codigoAmostra",
                "metodo",
                "registroInterno",
                "kit",
                "reteste",
                "loteKit",
                "dataProcessamentoFim",
                "valorReferencia",
                "observacao",
                "painel",
                "usuario",
                "timestamp",
            ]
            all_tests = set()
            for tests in self.panel_tests.values():
                all_tests.update(tests)
            final_cols = all_cols_base + sorted(list(all_tests))

            for col in final_cols:
                if col not in df_sucesso.columns:
                    df_sucesso[col] = None

            file_exists = (
                os.path.exists(caminho_historico)
                and os.path.getsize(caminho_historico) > 0
            )
            df_sucesso.to_csv(
                caminho_historico,
                mode="a",
                header=not file_exists,
                index=False,
                sep=";",
                encoding="utf-8-sig",
                columns=final_cols,
            )
            self.log(f"Histórico de {len(relatorio_final)} sucessos salvo.", "success")

        caminho_relatorio = os.path.join(log_dir, relatorio_filename)
        with open(caminho_relatorio, "w", encoding="utf-8") as f:
            f.write(
                f"Relatório de Envio ao GAL - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(f"Usuário: {usuario}\nKit: {kit}\nObservação: {observacao}\n\n")
            for item in relatorio_local:
                f.write(
                    f"- Amostra: {item['codigoAmostra']} (Paciente: {item['paciente']})\n"
                )
                f.write(f"  Status: {item['status']}\n")
                if item.get("erro"):
                    f.write(f"  Erros: {'; '.join(map(str, item['erro']))}\n")
                if item.get("campos_invalidos"):
                    invalidos_str = "; ".join(
                        [
                            f"{inv['campo']}='{inv['valor']}' ({inv['motivo']})"
                            for inv in item["campos_invalidos"]
                        ]
                    )
                    f.write(f"  Campos Inválidos: {invalidos_str}\n")
                f.write("\n")
        self.log(f"Relatório detalhado salvo em: {caminho_relatorio}", "info")


# ==============================================================================
# 3. CLASSE DE INTERFACE GRÁFICA (UI) - COM FEEDBACK MELHORADO
# ==============================================================================
class IntegrationApp(ctk.CTkToplevel):
    def __init__(self, master, usuario_logado: str, app_state: Optional[Any] = None):
        # Importar AfterManagerMixin dinamicamente para evitar circular imports
        from utils.after_mixin import AfterManagerMixin
        
        # Atualizar a herança com AfterManagerMixin no __init__
        # Como não podemos alterar a lista de herança aqui, vamos usar composição
        self._after_ids = set()
        
        super().__init__(master)
        self.title("Envio de Resultados para o GAL")
        self.geometry("900x800")

        self.usuario_logado = usuario_logado
        self.app_state = app_state
        self.gal_service = GalService(self.log_to_textbox)

        self.current_csv_path: Optional[str] = None
        self.observacao: str = ""
        self.relatorio_filename: str = ""
        
        # Flag para controle de thread em execução
        self._processing = False
        self._thread = None
        
        # Carrega config do exame se disponível
        self.exam_cfg = None
        if self.app_state:
            try:
                exame = getattr(self.app_state, "exame_selecionado", None)
                if exame:
                    self.exam_cfg = get_exam_cfg(exame)
            except Exception:
                self.exam_cfg = None

        self._criar_widgets()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _criar_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        top_frame.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(top_frame, text="Utilizador:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.usuario_entry = ctk.CTkEntry(top_frame)
        self.usuario_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(top_frame, text="Senha:").grid(
            row=0, column=2, padx=5, pady=5, sticky="w"
        )
        self.senha_entry = ctk.CTkEntry(top_frame, show="*")
        self.senha_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.csv_button = ctk.CTkButton(
            top_frame, text="Selecionar Arquivo CSV", command=self.selecionar_csv
        )
        self.csv_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.csv_label = ctk.CTkLabel(top_frame, text="Nenhum arquivo selecionado")
        self.csv_label.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

        self.start_button = ctk.CTkButton(
            top_frame,
            text="Iniciar Processamento",
            command=self.iniciar_processamento,
            state="disabled",
        )
        self.start_button.grid(
            row=2, column=0, columnspan=4, padx=5, pady=10, sticky="ew"
        )

        progress_frame = ctk.CTkFrame(self)
        progress_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        progress_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(progress_frame, text="Status: Pronto")
        self.status_label.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")

        self.progress_bar = ctk.CTkProgressBar(progress_frame, orientation="horizontal")
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="ew")

        log_frame = ctk.CTkFrame(self)
        log_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        self.log_text = ctk.CTkTextbox(log_frame, wrap="word")
        self.log_text.grid(row=0, column=0, sticky="nsew")
        self.log_text.configure(state="disabled")

    def _update_progress(self, text: str, value: float, color: str = "default"):
        def update():
            self.status_label.configure(text=f"Status: {text}")
            self.progress_bar.set(value)
            if color == "green":
                self.progress_bar.configure(progress_color="green")
            elif color == "red":
                self.progress_bar.configure(progress_color="red")
            else:
                self.progress_bar.configure(progress_color=["#3a7ebf", "#1f538d"])

        self.after(0, update)

    def log_to_textbox(self, message: str, level: str = "info"):
        level = level.lower()
        formatted_msg = (
            f"[{datetime.now().strftime('%H:%M:%S')}] {level.upper()}: {message}\n"
        )

        def update_log():
            self.log_text.configure(state="normal")
            color_map = {
                "error": "red",
                "warning": "orange",
                "critical": "darkred",
                "success": "green",
            }
            tag = color_map.get(level)
            if tag and tag not in self.log_text.tag_names():
                self.log_text.tag_config(tag, foreground=tag)

            self.log_text.insert("end", formatted_msg, tag if tag else None)
            self.log_text.see("end")
            self.log_text.configure(state="disabled")

        self.after(0, update_log)
        registrar_log("Envio GAL UI", message, level=level.upper())

    def selecionar_csv(self):
        path = filedialog.askopenfilename(
            title="Selecionar CSV de resultados", filetypes=[("CSV files", "*.csv")]
        )
        if not path:
            return

        self.current_csv_path = path
        self.csv_label.configure(text=os.path.basename(path))

        obs = simpledialog.askstring(
            "Observações",
            "Informe observações sobre esta corrida (opcional):",
            parent=self,
        )
        if obs is None:
            self.current_csv_path = None
            self.csv_label.configure(text="Nenhum arquivo selecionado")
            self.start_button.configure(state="disabled")
            return
        self.observacao = obs if obs else "Nenhuma observação."

        nome_relatorio = simpledialog.askstring(
            "Nome do Relatório",
            "Nome do arquivo para o relatório TXT:",
            initialvalue=f"relatorio_envio_{datetime.now().strftime('%Y%m%d_%H%M')}",
            parent=self,
        )
        self.relatorio_filename = (
            f"{nome_relatorio}.txt"
            if nome_relatorio
            else f"relatorio_envio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        self.start_button.configure(state="normal")
        self.log_to_textbox(
            f"Arquivo '{os.path.basename(path)}' pronto para envio.", "info"
        )

    def _on_close(self):
        """Fecha a janela com segurança, cancelando callbacks e threads."""
        try:
            # Cancelar todos os callbacks agendados (via AfterManagerMixin pattern)
            for aid in self._after_ids:
                try:
                    self.after_cancel(aid)
                except Exception:
                    pass
            self._after_ids.clear()
            
            # Avisar se há processamento em andamento
            if self._processing:
                resposta = messagebox.askyesno(
                    "Processamento em Andamento",
                    "Há um envio em andamento. Deseja realmente fechar?\n\n"
                    "Nota: O processamento continuará em segundo plano.",
                    parent=self
                )
                if not resposta:
                    return
            
            # Liberar grab se estiver ativo
            try:
                self.grab_release()
            except Exception:
                pass
            
            # Destruir janela
            if self.winfo_exists():
                self.destroy()
        except Exception as e:
            registrar_log("IntegrationApp", f"Erro ao fechar janela: {e}", "ERROR")
            # Forçar destruição em caso de erro
            try:
                self.destroy()
            except Exception:
                pass
    
    def schedule(self, delay_ms: int, callback, *args, **kwargs):
        """Agendar callback e registrar para cancelamento posterior."""
        aid = self.after(delay_ms, callback, *args, **kwargs)
        self._after_ids.add(aid)
        return aid
    
    def iniciar_processamento(self):
        usuario = self.usuario_entry.get().strip()
        senha = self.senha_entry.get().strip()
        if not all([usuario, senha, self.current_csv_path]):
            messagebox.showerror(
                "Dados Incompletos",
                "Utilizador, senha e arquivo CSV são obrigatórios.",
                parent=self,
            )
            return

        self._processing = True
        self._update_progress("A iniciar...", 0.0)
        self.start_button.configure(state="disabled")
        self.csv_button.configure(state="disabled")
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

        self._thread = threading.Thread(
            target=self._processar_em_background, args=(usuario, senha), daemon=True
        )
        self._thread.start()

    def _processar_em_background(self, usuario: str, senha: str):
        driver = None
        total_steps = 6
        try:
            self._update_progress(
                "Passo 1/6: A iniciar o navegador Firefox...", 1 / total_steps
            )
            driver = Firefox()

            self._update_progress(
                "Passo 2/6: A realizar login no GAL...", 2 / total_steps
            )
            self.gal_service.realizar_login(driver, usuario, senha)

            self._update_progress(
                "Passo 3/6: A ler e validar o arquivo CSV...", 3 / total_steps
            )
            df = self.gal_service.ler_csv_resultados(self.current_csv_path)
            if df is None:
                raise ValueError("Arquivo CSV inválido ou vazio.")

            self._update_progress(
                "Passo 4/6: A buscar metadados no GAL...", 4 / total_steps
            )
            kit = str(df.iloc[0]["kit"]) if not df.empty else "N/A"
            metas = self.gal_service.buscar_metadados(driver, set(df["codigoamostra"]))
            if not metas:
                raise ValueError("Nenhum metadado encontrado para as amostras.")

            relatorio_final, relatorio_local = [], []
            total_amostras = len(df)

            for i, (_, row) in enumerate(df.iterrows()):
                progress = (4 / total_steps) + (
                    (i + 1) / total_amostras * (1 / total_steps)
                )
                self._update_progress(
                    f"Passo 5/6: A enviar amostra {i+1} de {total_amostras}...",
                    progress,
                )
                ca = str(row.get("codigoamostra", ""))
                if ca in metas:
                    payload = self.gal_service.construir_payload(
                        metas[ca], row, self.observacao
                    )
                    resultado_envio = self.gal_service.enviar_amostra(driver, payload)
                    relatorio_local.append(resultado_envio)
                    if resultado_envio["status"] == "sucesso":
                        registro_sucesso = {
                            **payload,
                            "usuario": self.usuario_logado,
                            "timestamp": datetime.now().isoformat(),
                        }
                        relatorio_final.append(registro_sucesso)
                else:
                    relatorio_local.append(
                        {
                            "codigoAmostra": ca,
                            "paciente": "N/A",
                            "status": "nao_encontrado",
                            "erro": ["Metadados não encontrados no GAL"],
                            "campos_invalidos": [],
                        }
                    )

            self._update_progress("Passo 6/6: A salvar relatórios...", 6 / total_steps)
            self.gal_service.salvar_relatorios(
                relatorio_final,
                relatorio_local,
                self.usuario_logado,
                self.observacao,
                kit,
                self.relatorio_filename,
            )

            sucessos = sum(1 for r in relatorio_local if r["status"] == "sucesso")
            self._update_progress(
                f"Processamento concluído com {sucessos} sucesso(s)!", 1.0, "green"
            )

        except Exception as e:
            error_message = str(e).split("\n")[0]
            self._update_progress(f"ERRO CRÍTICO: {error_message}", 1.0, "red")
            self.log_to_textbox(f"ERRO CRÍTICO NO PROCESSAMENTO: {e}", "critical")
        finally:
            self._processing = False
            if driver:
                driver.quit()
            self.after(0, lambda: self.usuario_entry.delete(0, "end"))
            self.after(0, lambda: self.senha_entry.delete(0, "end"))
            self.after(0, lambda: self.start_button.configure(state="normal"))
            self.after(0, lambda: self.csv_button.configure(state="normal"))


# ==============================================================================
# 4. PONTO DE ENTRADA
# ==============================================================================
def abrir_janela_envio_gal(master, usuario_logado, app_state: Optional[Any] = None):
    janela = IntegrationApp(master, usuario_logado, app_state)
    janela.grab_set()
    return janela


if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    abrir_janela_envio_gal(root, "utilizador_de_teste")
    root.mainloop()