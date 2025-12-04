# autenticacao/auth_service.py
"""
Camada de autenticação de interface do IntegraGAL.

Papel:
- Expor uma API simples de login para a camada de UI (dialogs, telas de autenticação).
- Verificar credenciais a partir do arquivo de credenciais configurado (credenciais.csv),
  usando hashing seguro de senhas (bcrypt).
- No desenho de arquitetura, o AuthService é a "porta de entrada" da autenticação
  e pode, em evoluções futuras, delegar a gestão completa de usuários para
  core.authentication.user_manager.UserManager.
"""

import os
import sys

import bcrypt  # Nova dependência - adicione 'bcrypt' ao seu requirements.txt
import pandas as pd

# --- Configuração de Paths ---
from services.system_paths import BASE_DIR
from utils.io_utils import \
    read_data_with_auto_detection  # Reutilizamos o nosso leitor robusto
from utils.logger import registrar_log

# --- Constantes ---
CAMINHO_CREDENCIAIS = os.path.join(
    BASE_DIR, "banco", "credenciais.csv"
)  # MUDANÇA: de .xlsx para .csv


# --- Configuração de Paths Melhorada para Windows ---
# Tenta múltiplas formas de encontrar o diretório base
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # .../autenticacao
AUTH_DIR = os.path.dirname(SCRIPT_DIR)  # .../IntegragalGit
BASE_DIR = AUTH_DIR  # O BASE_DIR deve ser o diretório IntegragalGit

# Fallback: Se a estrutura não for a esperada, usa diretório atual
if not os.path.exists(os.path.join(BASE_DIR, "banco")):
    # Tenta encontrar o diretório IntegragalGit no diretório atual
    for item in os.listdir("."):
        if os.path.isdir(item) and item == "IntegragalGit":
            BASE_DIR = os.path.abspath(item)
            break
    else:
        # Se não encontrar, usa diretório atual
        BASE_DIR = os.getcwd()

# O BASE_DIR deve ser o diretório IntegragalGit, não o pai
if os.path.basename(BASE_DIR) != "IntegragalGit":
    possible_base = os.path.join(BASE_DIR, "IntegragalGit")
    if os.path.exists(possible_base):
        BASE_DIR = possible_base

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Importações
try:
    from utils.io_utils import read_data_with_auto_detection
    from utils.logger import registrar_log
except ImportError:
    # Fallback se não conseguir importar
    def registrar_log(modulo, mensagem, nivel="INFO"):
        print(f"[{nivel}] {modulo}: {mensagem}")

    def read_data_with_auto_detection(filepath):
        try:
            import pandas as pd

            # Fallback simples de leitura
            with open(filepath, "r", encoding="utf-8-sig") as f:
                content = f.read()
            return pd.read_csv(filepath, sep=";", encoding="utf-8-sig")
        except Exception:
            return None


# --- Constantes ---
CAMINHO_CREDENCIAIS = os.path.join(
    BASE_DIR, "banco", "usuarios.csv"
)  # Caminho absoluto


class AuthService:
    """
    Encapsula toda a lógica de negócio relacionada à autenticação e gestão de credenciais.
    """

    def __init__(self):
        self._criar_arquivo_se_nao_existir()

    def _criar_arquivo_se_nao_existir(self):
        """Garante que o arquivo de credenciais CSV exista."""
        if not os.path.exists(CAMINHO_CREDENCIAIS):
            try:
                # Cria diretório se não existir
                os.makedirs(os.path.dirname(CAMINHO_CREDENCIAIS), exist_ok=True)

                pd.DataFrame(columns=["usuario", "senha_hash"]).to_csv(
                    CAMINHO_CREDENCIAIS, index=False, sep=";"
                )
                registrar_log(
                    "AuthService",
                    f"Arquivo de credenciais criado em: {CAMINHO_CREDENCIAIS}",
                    "INFO",
                )
            except Exception as e:
                registrar_log(
                    "AuthService",
                    f"Falha ao criar arquivo de credenciais: {e}",
                    "CRITICAL",
                )

    def gerar_hash_bcrypt(self, senha: str) -> str:
        """
        Gera um hash seguro para a senha usando bcrypt.
        O salt é gerado e incluído automaticamente no hash.
        """
        senha_bytes = senha.encode("utf-8")
        hashed_bytes = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
        return hashed_bytes.decode("utf-8")

    def verificar_senha(self, usuario: str, senha_fornecida: str) -> bool:
        """
        Verifica se a senha fornecida corresponde ao hash armazenado para o utilizador.
        """
        try:
            registrar_log(
                "AuthService", f"Tentativa de login para usuário: {usuario}", "DEBUG"
            )

            # Tenta múltiplas formas de ler o arquivo
            df = None

            # Método 1: Usar o leitor automático
            df = read_data_with_auto_detection(CAMINHO_CREDENCIAIS)

            # Método 2: Fallback manual
            if df is None:
                registrar_log(
                    "AuthService", "Fallback: Tentando leitura manual do CSV", "WARNING"
                )
                try:
                    df = pd.read_csv(CAMINHO_CREDENCIAIS, sep=";", encoding="utf-8-sig")
                except Exception:
                    try:
                        df = pd.read_csv(CAMINHO_CREDENCIAIS, sep=";", encoding="utf-8")
                    except Exception:
                        try:
                            df = pd.read_csv(
                                CAMINHO_CREDENCIAIS, sep=";", encoding="latin-1"
                            )
                        except Exception as e:
                            registrar_log(
                                "AuthService",
                                f"Falha em todas as tentativas de leitura: {e}",
                                "ERROR",
                            )
                            return False

            if df is None or df.empty:
                registrar_log(
                    "AuthService",
                    "Arquivo de credenciais está vazio ou não pôde ser lido.",
                    "ERROR",
                )
                return False

            if "usuario" not in df.columns or "senha_hash" not in df.columns:
                registrar_log(
                    "AuthService",
                    f"Colunas necessárias não encontradas. "
                    f"Colunas presentes: {list(df.columns)}",
                    "ERROR",
                )
                return False

            # Comparação de usuário ignorando espaços e caixa
            credenciais_usuario = df[
                df["usuario"].str.strip().str.lower() == usuario.strip().lower()
            ]
            if credenciais_usuario.empty:
                registrar_log(
                    "AuthService", f"Usuário '{usuario}' não encontrado", "WARNING"
                )
                return False

            hash_armazenado_str = credenciais_usuario.iloc[0]["senha_hash"]
            hash_armazenado_bytes = hash_armazenado_str.encode("utf-8")
            senha_fornecida_bytes = senha_fornecida.encode("utf-8")

            # A função checkpw do bcrypt compara a senha com o hash (que já contém o salt)
            resultado = bcrypt.checkpw(senha_fornecida_bytes, hash_armazenado_bytes)
            registrar_log(
                "AuthService",
                f"Resultado da autenticação: {'Sucesso' if resultado else 'Falha'}",
                "INFO",
            )
            return resultado

        except Exception as e:
            registrar_log(
                "AuthService", f"Erro ao verificar credenciais: {e}", "CRITICAL"
            )
            return False
