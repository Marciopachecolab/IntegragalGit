# autenticacao/auth_service.py
import os
import sys
import pandas as pd
import bcrypt  # Nova dependência - adicione 'bcrypt' ao seu requirements.txt

# --- Configuração de Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from utils.logger import registrar_log
from utils.io_utils import read_data_with_auto_detection # Reutilizamos o nosso leitor robusto

# --- Constantes ---
CAMINHO_CREDENCIAIS = os.path.join(BASE_DIR, "banco", "credenciais.csv") # MUDANÇA: de .xlsx para .csv

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
                pd.DataFrame(columns=['usuario', 'senha_hash']).to_csv(CAMINHO_CREDENCIAIS, index=False, sep=';')
                registrar_log("AuthService", f"Arquivo de credenciais criado em: {CAMINHO_CREDENCIAIS}", "INFO")
            except Exception as e:
                registrar_log("AuthService", f"Falha ao criar arquivo de credenciais: {e}", "CRITICAL")
                
    def gerar_hash_bcrypt(self, senha: str) -> str:
        """
        Gera um hash seguro para a senha usando bcrypt.
        O salt é gerado e incluído automaticamente no hash.
        """
        senha_bytes = senha.encode('utf-8')
        hashed_bytes = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
        return hashed_bytes.decode('utf-8')

    def verificar_senha(self, usuario: str, senha_fornecida: str) -> bool:
        """
        Verifica se a senha fornecida corresponde ao hash armazenado para o utilizador.
        """
        try:
            df = read_data_with_auto_detection(CAMINHO_CREDENCIAIS)
            if df is None or 'usuario' not in df.columns or 'senha_hash' not in df.columns:
                registrar_log("AuthService", "Arquivo de credenciais é inválido ou está vazio.", "ERROR")
                return False

            credenciais_usuario = df[df['usuario'] == usuario]
            if credenciais_usuario.empty:
                registrar_log("AuthService", f"Tentativa de login para utilizador inexistente: '{usuario}'", "WARNING")
                return False

            hash_armazenado_str = credenciais_usuario.iloc[0]['senha_hash']
            hash_armazenado_bytes = hash_armazenado_str.encode('utf-8')
            senha_fornecida_bytes = senha_fornecida.encode('utf-8')
            
            # A função checkpw do bcrypt compara a senha com o hash (que já contém o salt)
            return bcrypt.checkpw(senha_fornecida_bytes, hash_armazenado_bytes)

        except Exception as e:
            registrar_log("AuthService", f"Erro ao verificar credenciais: {e}", "CRITICAL")
            return False