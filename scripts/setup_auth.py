#!/usr/bin/env python3
"""
Script de Configuração do Sistema de Autenticação IntegraGAL
Execute: python scripts/setup_auth.py

Autor: MiniMax Agent
Data: 2024-12-01
"""

import sys
import os
import bcrypt
from datetime import datetime

# Adicionar diretório pai ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Criar diretórios necessários
def criar_estrutura_diretorios():
    """Cria estrutura de diretórios necessária"""
    dirs = ['core', 'core/authentication', 'ui', 'services', 'storage', 'admin', 'scripts', 'banco', 'logs', 'assets', 'assets/icons']
    
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✅ Diretório criado/verificado: {dir_name}")

def criar_arquivos_csv():
    """Cria arquivos CSV com headers se não existirem"""
    
    # Arquivo de usuários
    usuarios_csv = "banco/usuarios.csv"
    if not os.path.exists(usuarios_csv):
        with open(usuarios_csv, 'w', encoding='utf-8') as f:
            f.write("id,usuario,senha_hash,nivel_acesso,status,data_criacao,ultimo_acesso,tentativas_falhas,bloqueado_ate,preferencias\n")
        print("✅ Arquivo usuarios.csv criado")
    else:
        print("📄 Arquivo usuarios.csv já existe")
    
    # Arquivo de sessões
    sessoes_csv = "banco/sessoes.csv"
    if not os.path.exists(sessoes_csv):
        with open(sessoes_csv, 'w', encoding='utf-8') as f:
            f.write("usuario_id,usuario_nome,nivel_acesso,token,data_criacao,ultimo_acesso,dados_contexto,ip_address,user_agent,status\n")
        print("✅ Arquivo sessoes.csv criado")
    else:
        print("📄 Arquivo sessoes.csv já existe")
    
    # Arquivo de configurações do sistema
    config_csv = "banco/configuracoes_sistema.csv"
    if not os.path.exists(config_csv):
        with open(config_csv, 'w', encoding='utf-8') as f:
            f.write("chave,valor,descricao,tipo,data_atualizacao,atualizado_por\n")
            f.write("versao_sistema,2.0.0,Versão atual do sistema,string,2024-12-01,admin_master\n")
            f.write("timeout_sessao,8,Tempo limite de sessão em horas,integer,2024-12-01,admin_master\n")
            f.write("max_tentativas_login,3,Número máximo de tentativas de login,integer,2024-12-01,admin_master\n")
            f.write("gal_base_url,https://galteste.saude.sc.gov.br,URL base do GAL,string,2024-12-01,admin_master\n")
            f.write("tema_padrao,claro,Tema padrão da interface,string,2024-12-01,admin_master\n")
        print("✅ Arquivo configuracoes_sistema.csv criado")
    else:
        print("📄 Arquivo configuracoes_sistema.csv já existe")
    
    # Arquivo de exames
    exames_csv = "banco/exames_config.csv"
    if not os.path.exists(exames_csv):
        with open(exames_csv, 'w', encoding='utf-8') as f:
            f.write("exame,modulo_analise,tipo_placa,numero_kit,equipamento,versao_regra,ativo,data_criacao\n")
            f.write("VR1,analise.vr1.analisar_placa_vr1,96,123,Equipamento X,1.0,TRUE,2024-12-01\n")
            f.write("VR2,analise.vr2.analisar_placa_vr2,96,124,Equipamento Y,1.0,TRUE,2024-12-01\n")
            f.write("VR1e2 Biomanguinhos 7500,analise.vr1e2_biomanguinhos_7500.analisar_placa_vr1e2_7500,48,7500,7500 Real-Time,1.0,TRUE,2024-12-01\n")
        print("✅ Arquivo exames_config.csv criado")
    else:
        print("📄 Arquivo exames_config.csv já existe")

def criar_user_manager():
    """Cria o arquivo UserManager.py"""
    user_manager_content = '''#!/usr/bin/env python3
"""
Sistema de Gerenciamento de Usuários com Controle Hierárquico
IntegraGAL v2.0
Autor: MiniMax Agent
Data: 2024-12-01
"""

import csv
import bcrypt
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class NivelAcesso(Enum):
    """Níveis de acesso hierárquicos"""
    ADMINISTRADOR = "ADMIN"
    MASTER = "MASTER" 
    DIAGNOSTICO = "DIAGNOSTICO"

class StatusUsuario(Enum):
    """Status possíveis do usuário"""
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    BLOQUEADO = "BLOQUEADO"
    EXPIRADO = "EXPIRADO"

@dataclass
class Usuario:
    """Estrutura de dados do usuário"""
    id: str
    usuario: str
    senha_hash: str
    nivel_acesso: NivelAcesso
    status: StatusUsuario
    data_criacao: str
    ultimo_acesso: str
    tentativas_falhas: int = 0
    bloqueado_ate: Optional[str] = None
    preferencias: Dict[str, Any] = None

class UserManager:
    """
    Gerenciador completo de usuários do sistema IntegraGAL
    Responsável por autenticação, autorização e gerenciamento de contas
    """
    
    def __init__(self, csv_path: str = "banco/usuarios.csv"):
        self.csv_path = csv_path
        self._garantir_arquivo_existe()
        self._session_timeout = timedelta(hours=8)  # 8 horas de sessão
        self._max_tentativas = 3
    
    def _garantir_arquivo_existe(self) -> None:
        """Garante que o arquivo CSV de usuários existe com headers"""
        try:
            with open(self.csv_path, 'x', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=[
                    'id', 'usuario', 'senha_hash', 'nivel_acesso', 'status',
                    'data_criacao', 'ultimo_acesso', 'tentativas_falhas', 
                    'bloqueado_ate', 'preferencias'
                ])
                writer.writeheader()
        except FileExistsError:
            pass  # Arquivo já existe
    
    def _carregar_usuarios(self) -> List[Usuario]:
        """Carrega usuários do arquivo CSV"""
        usuarios = []
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    usuario = Usuario(
                        id=row['id'],
                        usuario=row['usuario'],
                        senha_hash=row['senha_hash'],
                        nivel_acesso=NivelAcesso(row['nivel_acesso']),
                        status=StatusUsuario(row['status']),
                        data_criacao=row['data_criacao'],
                        ultimo_acesso=row['ultimo_acesso'],
                        tentativas_falhas=int(row.get('tentativas_falhas', 0)),
                        bloqueado_ate=row.get('bloqueado_ate'),
                        preferencias=self._parse_json(row.get('preferencias', '{}'))
                    )
                    usuarios.append(usuario)
        except Exception as e:
            print(f"Erro ao carregar usuários: {e}")
        return usuarios
    
    def _salvar_usuarios(self, usuarios: List[Usuario]) -> bool:
        """Salva lista de usuários no arquivo CSV"""
        try:
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=[
                    'id', 'usuario', 'senha_hash', 'nivel_acesso', 'status',
                    'data_criacao', 'ultimo_acesso', 'tentativas_falhas',
                    'bloqueado_ate', 'preferencias'
                ])
                writer.writeheader()
                
                for usuario in usuarios:
                    row = {
                        'id': usuario.id,
                        'usuario': usuario.usuario,
                        'senha_hash': usuario.senha_hash,
                        'nivel_acesso': usuario.nivel_acesso.value,
                        'status': usuario.status.value,
                        'data_criacao': usuario.data_criacao,
                        'ultimo_acesso': usuario.ultimo_acesso,
                        'tentativas_falhas': usuario.tentativas_falhas,
                        'bloqueado_ate': usuario.bloqueado_ate,
                        'preferencias': self._to_json(usuario.preferencias or {})
                    }
                    writer.writerow(row)
            return True
        except Exception as e:
            print(f"Erro ao salvar usuários: {e}")
            return False
    
    def _parse_json(self, json_str: str) -> Dict[str, Any]:
        """Parse string JSON de forma segura"""
        try:
            import json
            return json.loads(json_str) if json_str else {}
        except:
            return {}
    
    def _to_json(self, obj: Any) -> str:
        """Converte objeto para string JSON de forma segura"""
        try:
            import json
            return json.dumps(obj)
        except:
            return '{}'
    
    def autenticar(self, username: str, password: str, nivel_solicitado: str = None) -> Optional[Tuple[Usuario, str]]:
        """
        Autentica usuário no sistema
        Retorna tupla (usuario, token_sessao) ou None
        """
        usuarios = self._carregar_usuarios()
        
        # Buscar usuário
        usuario_encontrado = None
        for usuario in usuarios:
            if usuario.usuario.lower() == username.lower():
                usuario_encontrado = usuario
                break
        
        if not usuario_encontrado:
            return None
        
        # Verificar status
        if usuario_encontrado.status != StatusUsuario.ATIVO:
            return None
        
        # Verificar bloqueio
        if usuario_encontrado.bloqueado_ate:
            bloqueado_ate = datetime.strptime(usuario_encontrado.bloqueado_ate, '%Y-%m-%d %H:%M:%S')
            if datetime.now() < bloqueado_ate:
                return None
        
        # Verificar senha
        if not bcrypt.checkpw(password.encode('utf-8'), usuario_encontrado.senha_hash.encode('utf-8')):
            # Incrementar tentativas falhas
            usuario_encontrado.tentativas_falhas += 1
            
            # Bloquear após 3 tentativas
            if usuario_encontrado.tentativas_falhas >= self._max_tentativas:
                usuario_encontrado.status = StatusUsuario.BLOQUEADO
                usuario_encontrado.bloqueado_ate = (datetime.now() + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
            
            self._salvar_usuarios(usuarios)
            return None
        
        # Reset tentativas falhas
        usuario_encontrado.tentativas_falhas = 0
        usuario_encontrado.ultimo_acesso = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Verificar nível de acesso solicitado
        if nivel_solicitado:
            nivel_enum = NivelAcesso(nivel_solicitado.upper())
            hierarquia = {NivelAcesso.DIAGNOSTICO: 1, NivelAcesso.MASTER: 2, NivelAcesso.ADMINISTRADOR: 3}
            
            if hierarquia[usuario_encontrado.nivel_acesso] < hierarquia[nivel_enum]:
                return None
        
        # Gerar token de sessão
        token_sessao = self._gerar_token_sessao(usuario_encontrado)
        
        # Salvar alterações
        self._salvar_usuarios(usuarios)
        
        return usuario_encontrado, token_sessao
    
    def _gerar_token_sessao(self, usuario: Usuario) -> str:
        """Gera token único de sessão"""
        import secrets
        timestamp = datetime.now().timestamp()
        data = f"{usuario.id}:{usuario.usuario}:{timestamp}:{secrets.token_hex(16)}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    def criar_usuario(self, username: str, password: str, nivel_acesso: NivelAcesso, 
                     criador: str) -> Tuple[bool, str]:
        """
        Cria novo usuário (apenas ADMINISTRADOR)
        Retorna (sucesso, mensagem)
        """
        usuarios = self._carregar_usuarios()
        
        # Verificar se usuário já existe
        if any(u.usuario.lower() == username.lower() for u in usuarios):
            return False, "Usuário já existe"
        
        # Validar senha
        if len(password) < 8:
            return False, "Senha deve ter pelo menos 8 caracteres"
        
        # Hash da senha
        senha_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Criar novo usuário
        novo_usuario = Usuario(
            id=str(uuid.uuid4())[:8],
            usuario=username,
            senha_hash=senha_hash,
            nivel_acesso=nivel_acesso,
            status=StatusUsuario.ATIVO,
            data_criacao=datetime.now().strftime('%Y-%m-%d'),
            ultimo_acesso=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            preferencias={'tema': 'claro', 'idioma': 'pt_BR', 'notificacoes': True}
        )
        
        usuarios.append(novo_usuario)
        
        if self._salvar_usuarios(usuarios):
            return True, f"Usuário '{username}' criado com sucesso"
        else:
            return False, "Erro ao salvar usuário"
    
    def listar_usuarios(self, filtro_status: StatusUsuario = None) -> List[Usuario]:
        """Lista usuários com filtro opcional por status"""
        usuarios = self._carregar_usuarios()
        
        if filtro_status:
            usuarios = [u for u in usuarios if u.status == filtro_status]
        
        return usuarios

def inicializar_sistema():
    """Inicializa o sistema com usuário administrador padrão"""
    user_manager = UserManager()
    usuarios = user_manager._carregar_usuarios()
    
    # Criar administrador padrão se não existir
    if not any(u.nivel_acesso == NivelAcesso.ADMINISTRADOR for u in usuarios):
        sucesso, msg = user_manager.criar_usuario(
            username="admin",
            password="admin123456",
            nivel_acesso=NivelAcesso.ADMINISTRADOR,
            criador="sistema"
        )
        if sucesso:
            print(f"✅ {msg}")
            print("🔑 Credenciais padrão: admin / admin123456")
        else:
            print(f"❌ {msg}")
    else:
        print("📋 Administrador já existe no sistema")

if __name__ == "__main__":
    inicializar_sistema()
'''
    
    with open("core/authentication/user_manager.py", "w", encoding="utf-8") as f:
        f.write(user_manager_content)
    print("✅ Arquivo UserManager.py criado")

def configurar_usuarios_iniciais():
    """Configura usuários iniciais do sistema"""
    from core.authentication.user_manager import UserManager, NivelAcesso
    
    user_manager = UserManager()
    
    print("🔧 Configurando usuários iniciais do IntegraGAL...")
    
    # Verificar se já existem usuários
    usuarios_existentes = user_manager.listar_usuarios()
    if usuarios_existentes:
        print(f"📋 Encontrados {len(usuarios_existentes)} usuários existentes:")
        for u in usuarios_existentes:
            print(f"   - {u.usuario} ({u.nivel_acesso.value})")
        return
    
    # Usuário Administrador Master
    sucesso, msg = user_manager.criar_usuario(
        username="admin_master",
        password="Admin@123456",
        nivel_acesso=NivelAcesso.ADMINISTRADOR,
        criador="sistema"
    )
    print(f"{'✅' if sucesso else '❌'} Admin Master: {msg}")
    
    # Usuário Master
    if sucesso:  # Só criar se o admin foi criado
        sucesso, msg = user_manager.criar_usuario(
            username="lab_supervisor",
            password="Supervisor@123",
            nivel_acesso=NivelAcesso.MASTER,
            criador="admin_master"
        )
        print(f"{'✅' if sucesso else '❌'} Lab Supervisor: {msg}")
        
        # Usuário Diagnóstico
        sucesso, msg = user_manager.criar_usuario(
            username="tecnico_lab",
            password="Tecnico@123",
            nivel_acesso=NivelAcesso.DIAGNOSTICO,
            criador="admin_master"
        )
        print(f"{'✅' if sucesso else '❌'} Técnico Lab: {msg}")
    
    print("\n🎯 Configuração concluída!")
    if usuarios_existentes:
        print("📋 Usuários mantidos (já existiam):")
    else:
        print("📋 Credenciais padrão criadas:")
        print("   👑 Admin: admin_master / Admin@123456")
        print("   🔧 Master: lab_supervisor / Supervisor@123")
        print("   🧪 Técnico: tecnico_lab / Tecnico@123")

def main():
    """Função principal"""
    print("🧬 IntegraGAL v2.0 - Configuração do Sistema de Autenticação")
    print("=" * 60)
    
    try:
        # Passo 1: Criar estrutura
        print("\n1️⃣ Criando estrutura de diretórios...")
        criar_estrutura_diretorios()
        
        # Passo 2: Criar arquivos CSV
        print("\n2️⃣ Criando arquivos CSV (bancos de dados)...")
        criar_arquivos_csv()
        
        # Passo 3: Criar UserManager
        print("\n3️⃣ Criando sistema de autenticação...")
        criar_user_manager()
        
        # Passo 4: Configurar usuários iniciais
        print("\n4️⃣ Configurando usuários iniciais...")
        configurar_usuarios_iniciais()
        
        print("\n" + "=" * 60)
        print("🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("\n📋 Próximos passos:")
        print("   1. Testar autenticação: python -c 'from core.authentication.user_manager import UserManager; um = UserManager(); print(um.listar_usuarios())'")
        print("   2. Executar interface de login (quando disponível)")
        print("   3. Configurar módulos adicionais")
        
    except Exception as e:
        print(f"\n❌ ERRO durante configuração: {e}")
        print("🔧 Verifique se:")
        print("   - Ambiente virtual está ativo")
        print("   - Permissões de escrita no diretório")
        print("   - Dependências estão instaladas")
        return False
    
    return True

if __name__ == "__main__":
    main()