# /Integragal/config.py
import json
import os
import pathlib

# Define o diretÃ³rio base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "configuracao", "config.json")

# Define o diretÃ³rio para logs e arquivos de histÃ³rico
DATA_DIR = os.path.join(BASE_DIR, "dados")
LOG_FILE_PATH = os.path.join(DATA_DIR, "sistema.log")
TOTAL_IMPORTADOS_PATH = os.path.join(DATA_DIR, "total_importados_gal.csv")

def carregar_config():
    """
    Carrega as configuraÃ§Ãµes do arquivo config.json.
    Se o arquivo nÃ£o existir, gera um arquivo de configuraÃ§Ã£o padrÃ£o.
    """
    if not os.path.exists(CONFIG_FILE):
        return gerar_config_padrao()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON do arquivo de configuraÃ§Ã£o: {e}")
        print("Gerando configuraÃ§Ã£o padrÃ£o...")
        return gerar_config_padrao()
    except Exception as e:
        print(f"Erro ao carregar arquivo de configuraÃ§Ã£o: {e}")
        print("Gerando configuraÃ§Ã£o padrÃ£o...")
        return gerar_config_padrao()

def salvar_config(config):
    """
    Salva o dicionÃ¡rio de configuraÃ§Ã£o no arquivo config.json.
    Cria o diretÃ³rio 'configuracao' se nÃ£o existir.
    """
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def gerar_config_padrao():
    """
    Gera e salva um dicionÃ¡rio com configuraÃ§Ãµes padrÃ£o para a aplicaÃ§Ã£o.
    Inclui configuraÃ§Ãµes de diretÃ³rios, GAL, laboratÃ³rio, exames e PostgreSQL.
    """
    config = {
        "diretorios": {
            "pasta_csv": str(pathlib.Path.home() / "Desktop" / "Integragal_CSVs"),
            "pasta_resultados": str(pathlib.Path.home() / "Desktop" / "Integragal_Resultados")
        },
        "gal": {
            "base_url": "https://galteste.saude.sc.gov.br",
            "url_envio": "https://galteste.saude.sc.gov.br/bmh/entrada-resultados/gravar/",
            "usuario_padrao": "",
            "senha_padrao": "",
            "max_retries": 3,
            "retry_delay": 2,
            "request_timeout": 30,
            "geckodriver_path": ""
        },
        "laboratorio": {
            "nome": "LACEN",
            "responsavel": "ResponsÃ¡vel TÃ©cnico"
        },
        "exames_ativos": ["VR1", "VR2", "Arboviroses", "VÃ­rus RespiratÃ³rios", "VR1e2 Biomanguinhos 7500"],
        "exames_config": {
            "VR1": {
                "kit_codigo": 100,
                "export_fields": ["SC2", "Inf A", "Inf B"]
            },
            "VR2": {
                "kit_codigo": 200,
                "export_fields": ["ADV", "RSV", "HRV"]
            },
            "Arboviroses": {
                "kit_codigo": 893,
                "export_fields": ["dengue", "chikungunya", "zika", "denguect", "chikungunyact", "zikact", "sorotipo"]
            },
            "VÃ­rus RespiratÃ³rios": {
                "kit_codigo": 427,
                "export_fields": [
                    "influenzaa", "influenzab", "coronavirusncov", "coronavirus229e",
                    "coronavirusnl63", "coronavirushku1", "coronavirusoc43", "adenovirus",
                    "vsincicialresp", "metapneumovirus", "rinovirus", "bocavirus",
                    "enterovirus", "parainflu_1", "parainflu_2", "parainflu_3", "parainflu_4",
                    "coronavirus", "influenzaahn", "metapneumovirua", "metapneumovirub",
                    "mycoplasma", "parechovÃ­rus", "vsincicialrespa", "vsincicialrespb",
                    "influenzaah_3", "influenzaah_5", "influenzaah_7"
                ]
            },
            "VR1e2 Biomanguinhos 7500": {
                "kit_codigo": 1140,
                "export_fields": [
                    "Sars-Cov-2", "Influenzaa", "influenzab", "RSV",
                    "adenovÃ­rus", "metapneumovirus", "rinovÃ­rus"
                ]
            }
        },
        "painel_tests_gal": {
            "1": [
                "influenzaa", "influenzab", "coronavirusncov", "coronavirus229e",
                "coronavirusnl63", "coronavirushku1", "coronavirusoc43", "adenovirus",
                "vsincicialresp", "metapneumovirus", "rinovirus", "bocavirus",
                "enterovirus", "parainflu_1", "parainflu_2", "parainflu_3", "parainflu_4",
                "coronavirus", "influenzaahn", "metapneumovirua", "metapneumovirub",
                "mycoplasma", "parechovÃ­rus", "vsincicialrespa", "vsincicialrespb",
                "influenzaah_3", "influenzaah_5", "influenzaah_7"
            ]
        },
        "postgres": {
            "dbname": "seu_banco",
            "user": "seu_usuario",
            "password": "sua_senha",
            "host": "localhost",
            "port": "5432"
        }
    }
    salvar_config(config)
    return config

# Garante que o diretÃ³rio de dados exista ao iniciar
os.makedirs(DATA_DIR, exist_ok=True)
