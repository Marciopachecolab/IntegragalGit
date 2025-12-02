# services/config_service.py
import json
import os
import sys
from typing import Dict, Any

# --- Configuração de Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from utils.logger import registrar_log

# O único ficheiro de configuração que a aplicação irá conhecer
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

class ConfigService:
    """
    Classe singleton para gerir todas as configurações da aplicação a partir de um único ficheiro.
    """
    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Carrega a configuração ou cria um ficheiro padrão."""
        if not self._config: # Carrega apenas uma vez
            if not os.path.exists(CONFIG_PATH):
                registrar_log("ConfigService", f"Ficheiro de configuração não encontrado. A criar '{CONFIG_PATH}' padrão.", "WARNING")
                self._config = self._get_default_config()
                self._save_config()
            else:
                try:
                    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                        self._config = json.load(f)
                    registrar_log("ConfigService", "Configurações carregadas com sucesso.", "INFO")
                except json.JSONDecodeError as e:
                    registrar_log("ConfigService", f"Erro ao ler o config.json: {e}. A carregar configuração padrão.", "ERROR")
                    self._config = self._get_default_config()
                except Exception as e:
                    registrar_log("ConfigService", f"Erro inesperado ao carregar config: {e}", "CRITICAL")
                    self._config = self._get_default_config()

    def get(self, key: str, default: Any = None) -> Any:
        """Obtém uma chave de configuração de alto nível."""
        return self._config.get(key, default)

    def get_db_config(self) -> Dict[str, Any]:
        """Retorna a secção de configuração da base de dados."""
        return self.get("postgres", {})
    
    def get_gal_config(self) -> Dict[str, Any]:
        """Retorna a secção de configuração do GAL."""
        return self.get("gal_integration", {})

    def get_paths(self) -> Dict[str, str]:
        """Retorna a secção de caminhos e diretórios."""
        paths = self.get("paths", {})
        # Garante que os caminhos sejam absolutos a partir do BASE_DIR
        for key, value in paths.items():
            if not os.path.isabs(value):
                paths[key] = os.path.join(BASE_DIR, value)
        return paths

    def _save_config(self):
        """Salva a configuração atual no ficheiro JSON."""
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            registrar_log("ConfigService", f"Não foi possível salvar o ficheiro de configuração: {e}", "CRITICAL")

    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna a estrutura de configuração padrão completa."""
        return {
            "paths": {
                "log_file": "logs/sistema.log",
                "exams_catalog_csv": "banco/exames_config.csv",
                "credentials_csv": "banco/credenciais.csv",
                "gal_history_csv": "logs/total_importados_gal.csv"
            },
            "postgres": {
                "enabled": False,
                "dbname": "integragal",
                "user": "postgres",
                "password": "your_password_here",
                "host": "localhost",
                "port": 5432
            },
            "gal_integration": {
                "base_url": "https://galteste.saude.sc.gov.br",
                "login_ids": {
                    "username": "usuario",
                    "password": "senha",
                    "module_button": "ext-gen17",
                    "lab_button": "ext-gen25",
                    "login_button": "ext-gen29"
                },
                "api_endpoints": {
                    "metadata": "/bmh/entrada-resultados/lista/",
                    "submit": "/bmh/entrada-resultados/gravar/"
                },
                "retry_settings": {
                    "max_retries": 3,
                    "backoff_factor": 0.5
                },
                "panel_tests": {
                    "1": [
                        "influenzaa", "influenzab", "coronavirusncov", "coronavirus229e",
                        "coronavirusnl63", "coronavirushku1", "coronavirusoc43", "adenovirus",
                        "vsincicialresp", "metapneumovirus", "rinovirus", "bocavirus",
                        "enterovirus", "parainflu_1", "parainflu_2", "parainflu_3", "parainflu_4"
                    ]
                }
            }
        }

# Instância única para ser usada em toda a aplicação
config_service = ConfigService()