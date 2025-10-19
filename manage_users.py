# manage_users.py
import pandas as pd
import getpass
import os
import sys

# --- Configuração de Paths ---
# Adiciona o diretório do projeto ao path para poder importar o AuthService
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from autenticacao.auth_service import AuthService, CAMINHO_CREDENCIAIS

def adicionar_ou_atualizar_usuario():
    """
    Ferramenta de linha de comando para adicionar um novo utilizador ou atualizar a senha de um existente.
    """
    print("--- Gestão de Utilizadores do IntegraGAL ---")
    
    try:
        # Pede o nome de utilizador
        usuario = input("Digite o nome do utilizador: ").strip()
        if not usuario:
            print("Erro: O nome de utilizador não pode estar em branco.")
            return

        # Pede a senha de forma segura (não mostra no ecrã)
        senha = getpass.getpass("Digite a nova senha: ")
        if not senha:
            print("Erro: A senha não pode estar em branco.")
            return
            
        senha_confirm = getpass.getpass("Confirme a nova senha: ")
        if senha != senha_confirm:
            print("Erro: As senhas não coincidem.")
            return

        # Usa o AuthService para gerar o hash
        auth = AuthService()
        hash_senha = auth.gerar_hash_bcrypt(senha)
        
        # Lê o arquivo de credenciais existente
        if os.path.exists(CAMINHO_CREDENCIAIS):
            df = pd.read_csv(CAMINHO_CREDENCIAIS, sep=';')
        else:
            df = pd.DataFrame(columns=['usuario', 'senha_hash'])

        # Verifica se o utilizador já existe para atualizar ou adicionar
        if usuario in df['usuario'].values:
            # Atualiza a senha do utilizador existente
            df.loc[df['usuario'] == usuario, 'senha_hash'] = hash_senha
            print(f"Senha do utilizador '{usuario}' atualizada com sucesso.")
        else:
            # Adiciona o novo utilizador
            novo_user = pd.DataFrame([{'usuario': usuario, 'senha_hash': hash_senha}])
            df = pd.concat([df, novo_user], ignore_index=True)
            print(f"Utilizador '{usuario}' adicionado com sucesso.")

        # Salva o arquivo CSV atualizado
        df.to_csv(CAMINHO_CREDENCIAIS, index=False, sep=';')
        print(f"Arquivo de credenciais '{CAMINHO_CREDENCIAIS}' salvo.")

    except Exception as e:
        print(f"\nOcorreu um erro: {e}")

if __name__ == "__main__":
    adicionar_ou_atualizar_usuario()