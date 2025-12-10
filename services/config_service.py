# services/config_service.py
"""
ConfigService - API Única para Configurações do Sistema

⚠️ IMPORTANTE: Esta é a ÚNICA forma oficial de acessar configurações.
   NUNCA leia config.json diretamente com open(). Use os métodos desta classe.

API Principal:
    - config_service.get(key, default=None) - Lê configuração
    - config_service.set(key, value) - Escreve configuração
    - config_service.get_db_config() - Config do PostgreSQL
    - config_service.get_gal_config() - Config do GAL
    - config_service.get_paths() - Caminhos do sistema

Exemplo de Uso:
    from services.config_service import config_service
    
    # Ler
    laboratorio = config_service.get('laboratorio', 'Padrão')
    
    # Escrever
    config_service.set('laboratorio', 'Novo Nome')

Ver: RELATORIO_REDUNDANCIA_CONFLITOS.md (FASE 3, Etapa 3.3)
"""

import json
import os
from typing import Any, Dict
import warnings

# --- Configuração de Paths ---
from services.system_paths import BASE_DIR
from utils.logger import registrar_log

# O único ficheiro de configuração que a aplicação irá conhecer
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")


# Sistema de monitoramento (opcional, ativado apenas em debug)
_MONITORED_MODE = __debug__

def _warn_direct_config_access():
    """Emite warning se houver acesso direto ao config.json."""
    if _MONITORED_MODE:
        warnings.warn(
            "Leitura direta de config.json detectada. Use config_service.get() em vez disso. "
            "Ver documentação em services/config_service.py",
            DeprecationWarning,
            stacklevel=3
        )





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

        if not self._config:  # Carrega apenas uma vez

            if not os.path.exists(CONFIG_PATH):

                registrar_log(

                    "ConfigService",

                    f"Ficheiro de configuração não encontrado. A criar '{CONFIG_PATH}' padrão.",

                    "WARNING",

                )

                self._config = self._get_default_config()

                self._save_config()

            else:

                try:

                    with open(CONFIG_PATH, "r", encoding="utf-8") as f:

                        self._config = json.load(f)

                    registrar_log(

                        "ConfigService", "Configurações carregadas com sucesso.", "INFO"

                    )

                except json.JSONDecodeError as e:

                    registrar_log(

                        "ConfigService",

                        f"Erro ao ler o config.json: {e}. A carregar configuração padrão.",

                        "ERROR",

                    )

                    self._config = self._get_default_config()

                except Exception as e:

                    registrar_log(

                        "ConfigService",

                        f"Erro inesperado ao carregar config: {e}",

                        "CRITICAL",

                    )

                    self._config = self._get_default_config()



    def get(self, key: str, default: Any = None) -> Any:

        """Obtém uma chave de configuração de alto nível."""

        return self._config.get(key, default)

    
    def set(self, key: str, value: Any):
        """
        Define uma chave de configuração de alto nível.
        
        Args:
            key: Chave da configuração
            value: Valor a ser definido
        
        Nota: Não salva automaticamente. Use save() para persistir.
        """
        self._config[key] = value
        registrar_log(
            "ConfigService",
            f"Configuração '{key}' atualizada para: {value}",
            "INFO"
        )
    
    
    def save(self):
        """
        Salva as configurações atuais no arquivo config.json.
        
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        self._save_config()
        return True



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

            registrar_log(

                "ConfigService",

                f"Não foi possível salvar o ficheiro de configuração: {e}",

                "CRITICAL",

            )



    def _get_default_config(self) -> Dict[str, Any]:

        """Retorna a estrutura de configuração padrão completa."""

        return {

            "paths": {

                "log_file": "logs/sistema.log",

                "exams_catalog_csv": "banco/exames_config.csv",

                "credentials_csv": "banco/credenciais.csv",

                "gal_history_csv": "logs/total_importados_gal.csv",

            },

            "postgres": {

                "enabled": False,

                "dbname": "integragal",

                "user": "postgres",

                "password": "your_password_here",

                "host": "localhost",

                "port": 5432,

            },

            "gal_integration": {

                "base_url": "https://galteste.saude.sc.gov.br",

                "login_ids": {

                    "username": "usuario",

                    "password": "senha",

                    "module_button": "ext-gen17",

                    "lab_button": "ext-gen25",

                    "login_button": "ext-gen29",

                },

                "api_endpoints": {

                    "metadata": "/bmh/entrada-resultados/lista/",

                    "submit": "/bmh/entrada-resultados/gravar/",

                },

                "retry_settings": {"max_retries": 3, "backoff_factor": 0.5},

                "panel_tests": {

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

                    ]

                },

            },

        }





# Instância única para ser usada em toda a aplicação

config_service = ConfigService()

