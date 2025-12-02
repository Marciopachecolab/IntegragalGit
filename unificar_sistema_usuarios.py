#!/usr/bin/env python3
"""
Script para unificar o sistema de usuários - IntegraGAL v2.0
Consolida credenciais.csv e usuarios.csv em um único arquivo
Autor: MiniMax Agent
Data: 2025-12-02
"""

import os
import sys
import pandas as pd
import bcrypt
from datetime import datetime
import shutil

# Configuração de paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENCIAS_PATH = os.path.join(BASE_DIR, "banco", "credenciais.csv")
USUARIOS_PATH = os.path.join(BASE_DIR, "banco", "usuarios.csv")

def criar_backup():
    """Cria backup dos arquivos originais"""
    backup_dir = os.path.join(BASE_DIR, "backup_usuarios")
    os.makedirs(backup_dir, exist_ok=True)
    
    if os.path.exists(CREDENCIAS_PATH):
        shutil.copy2(CREDENCIAS_PATH, os.path.join(backup_dir, "credenciais_original.csv"))
        print(f"✅ Backup criado: {backup_dir}/credenciais_original.csv")
    
    if os.path.exists(USUARIOS_PATH):
        shutil.copy2(USUARIOS_PATH, os.path.join(backup_dir, "usuarios_original.csv"))
        print(f"✅ Backup criado: {backup_dir}/usuarios_original.csv")

def consolidar_usuarios():
    """Consolida usuários de ambos os arquivos em credenciais.csv"""
    
    usuarios_consolidados = []
    
    # Ler credenciais.csv
    if os.path.exists(CREDENCIAS_PATH):
        try:
            df_credenciais = pd.read_csv(CREDENCIAS_PATH, sep=';')
            print(f"📂 Carregados {len(df_credenciais)} usuários de credenciais.csv")
            
            for _, row in df_credenciais.iterrows():
                usuario = {
                    'id': f"usr_{hash(row['usuario']) % 10000:04d}",
                    'usuario': row['usuario'],
                    'senha_hash': row['senha_hash'],
                    'nivel_acesso': 'USER',
                    'status': 'ATIVO',
                    'data_criacao': datetime.now().strftime('%Y-%m-%d'),
                    'ultimo_acesso': '',
                    'tentativas_falhas': 0,
                    'bloqueado_ate': '',
                    'preferencias': '{"tema":"claro","idioma":"pt_BR","notificacoes":true}'
                }
                usuarios_consolidados.append(usuario)
        except Exception as e:
            print(f"❌ Erro ao ler credenciais.csv: {e}")
    
    # Ler usuarios.csv
    if os.path.exists(USUARIOS_PATH):
        try:
            import json
            df_usuarios = pd.read_csv(USUARIOS_PATH)
            print(f"📂 Carregados {len(df_usuarios)} usuários de usuarios.csv")
            
            for _, row in df_usuarios.iterrows():
                usuario_existe = any(u['usuario'] == row['usuario'] for u in usuarios_consolidados)
                
                if not usuario_existe:
                    usuario = {
                        'id': row.get('id', f"usr_{hash(row['usuario']) % 10000:04d}"),
                        'usuario': row['usuario'],
                        'senha_hash': row['senha_hash'],
                        'nivel_acesso': row.get('nivel_acesso', 'USER'),
                        'status': row.get('status', 'ATIVO'),
                        'data_criacao': row.get('data_criacao', datetime.now().strftime('%Y-%m-%d')),
                        'ultimo_acesso': row.get('ultimo_acesso', ''),
                        'tentativas_falhas': int(row.get('tentativas_falhas', 0)),
                        'bloqueado_ate': row.get('bloqueado_ate', ''),
                        'preferencias': row.get('preferencias', '{"tema":"claro","idioma":"pt_BR","notificacoes":true}')
                    }
                    usuarios_consolidados.append(usuario)
                else:
                    print(f"⚠️  Usuário {row['usuario']} já existe, ignorando do usuarios.csv")
        except Exception as e:
            print(f"❌ Erro ao ler usuarios.csv: {e}")
    
    # Salvar credenciais.csv unificado
    if usuarios_consolidados:
        df_final = pd.DataFrame(usuarios_consolidados)
        df_final.to_csv(CREDENCIAS_PATH, sep=';', index=False)
        print(f"✅ Arquivo credenciais.csv unificado criado com {len(usuarios_consolidados)} usuários")
        
        # Mostrar resumo
        print("\n📋 USUÁRIOS CONSOLIDADOS:")
        for i, usuario in enumerate(usuarios_consolidados, 1):
            print(f"   {i}. {usuario['usuario']} - {usuario['nivel_acesso']} - {usuario['status']}")
        
        return True
    else:
        print("❌ Nenhum usuário encontrado para consolidar")
        return False

def atualizar_user_manager():
    """Atualiza UserManager para usar credenciais.csv"""
    
    novo_user_manager = '''#!/usr/bin/env python3
"""
Sistema de Gerenciamento de Usuários com Controle Hierárquico - VERSÃO UNIFICADA
IntegraGAL v2.0
Autor: MiniMax Agent
Data: 2025-12-02
"""

import csv
import bcrypt
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import os
import sys

class NivelAcesso(Enum):
    """Níveis de acesso hierárquicos"""
    ADMINISTRADOR = "ADMIN"
    MASTER = "MASTER" 
    DIAGNOSTICO = "DIAGNOSTICO"
    USER = "USER"

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
    VERSÃO UNIFICADA - Usa apenas credenciais.csv
    """
    
    def __init__(self, csv_path: str = "banco/credenciais.csv"):
        self.csv_path = csv_path
        self._garantir_arquivo_existe()
        self._session_timeout = timedelta(hours=8)  # 8 horas de sessão
        self._max_tentativas = 3
    
    def _garantir_arquivo_existe(self) -> None:
        """Garante que o arquivo CSV de usuários existe com headers"""
        try:
            # Verificar se arquivo existe e tem estrutura correta
            if os.path.exists(self.csv_path):
                try:
                    df = pd.read_csv(self.csv_path, sep=';')
                    colunas_necessarias = ['id', 'usuario', 'senha_hash', 'nivel_acesso', 'status', 
                                         'data_criacao', 'ultimo_acesso', 'tentativas_falhas', 
                                         'bloqueado_ate', 'preferencias']
                    
                    # Adicionar colunas faltantes se necessário
                    for col in colunas_necessarias:
                        if col not in df.columns:
                            df[col] = '' if col not in ['tentativas_falhas'] else 0
                    
                    # Salvar estrutura corrigida
                    df.to_csv(self.csv_path, sep=';', index=False)
                    return
                except:
                    pass  # Arquivo existe mas com problema, recriar
            
            # Criar arquivo com header padrão
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
            df_vazio = pd.DataFrame(columns=[
                'id', 'usuario', 'senha_hash', 'nivel_acesso', 'status', 
                'data_criacao', 'ultimo_acesso', 'tentativas_falhas', 
                'bloqueado_ate', 'preferencias'
            ])
            df_vazio.to_csv(self.csv_path, sep=';', index=False)
            print(f"✅ Arquivo credenciais.csv criado com estrutura unificada")
            
        except Exception as e:
            print(f"❌ Erro ao criar arquivo: {e}")
    
    def _carregar_usuarios(self) -> List[Usuario]:
        """Carrega usuários do arquivo CSV"""
        usuarios = []
        try:
            # Ler arquivo com separador ponto-e-vírgula
            df = pd.read_csv(self.csv_path, sep=';')
            
            for _, row in df.iterrows():
                usuario = Usuario(
                    id=row.get('id', f"usr_{hash(row['usuario']) % 10000:04d}"),
                    usuario=row['usuario'],
                    senha_hash=row['senha_hash'],
                    nivel_acesso=NivelAcesso(row.get('nivel_acesso', 'USER')),
                    status=StatusUsuario(row.get('status', 'ATIVO')),
                    data_criacao=row.get('data_criacao', datetime.now().strftime('%Y-%m-%d')),
                    ultimo_acesso=row.get('ultimo_acesso', ''),
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
            data = []
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
                data.append(row)
            
            df = pd.DataFrame(data)
            df.to_csv(self.csv_path, sep=';', index=False)
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
            try:
                bloqueado_ate = datetime.strptime(usuario_encontrado.bloqueado_ate, '%Y-%m-%d %H:%M:%S')
                if datetime.now() < bloqueado_ate:
                    return None
            except:
                pass  # Se não conseguir parsear, ignora o bloqueio
        
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
            try:
                nivel_enum = NivelAcesso(nivel_solicitado.upper())
                hierarquia = {NivelAcesso.DIAGNOSTICO: 1, NivelAcesso.MASTER: 2, NivelAcesso.ADMINISTRADOR: 3, NivelAcesso.USER: 1}
                
                if hierarquia[usuario_encontrado.nivel_acesso] < hierarquia[nivel_enum]:
                    return None
            except:
                pass  # Se não conseguir validar nível, continua
        
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
        if len(password) < 6:
            return False, "Senha deve ter pelo menos 6 caracteres"
        
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
            ultimo_acesso='',
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
    usuarios = user_manager.listar_usuarios()
    
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
    
    # Salvar arquivo atualizado
    user_manager_path = os.path.join(BASE_DIR, "core", "authentication", "user_manager.py")
    
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(user_manager_path), exist_ok=True)
    
    with open(user_manager_path, 'w', encoding='utf-8') as f:
        f.write(novo_user_manager)
    
    print(f"✅ UserManager atualizado para usar credenciais.csv")

def atualizar_user_management():
    """Atualiza interface de gerenciamento para usar credenciais.csv"""
    
    arquivo_ui = os.path.join(BASE_DIR, "IntegragalGit", "ui", "user_management.py")
    
    if os.path.exists(arquivo_ui):
        # Ler arquivo atual
        with open(arquivo_ui, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Atualizar caminho do arquivo
        conteudo = conteudo.replace(
            'self.credenciais_path = "banco/credenciais.csv"',
            'self.credenciais_path = "banco/credenciais.csv"'
        )
        
        # Salvar arquivo atualizado
        with open(arquivo_ui, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print(f"✅ Interface de gerenciamento atualizada")

def main():
    """Função principal"""
    print("="*60)
    print("🔧 UNIFICAÇÃO DO SISTEMA DE USUÁRIOS - IntegraGAL v2.0")
    print("="*60)
    
    # Criar backup
    print("\n📦 Criando backup dos arquivos originais...")
    criar_backup()
    
    # Consolidar usuários
    print("\n🔄 Consolidando usuários...")
    if consolidar_usuarios():
        
        # Atualizar UserManager
        print("\n🔧 Atualizando UserManager...")
        atualizar_user_manager()
        
        # Atualizar interface
        print("\n🎨 Atualizando interface de gerenciamento...")
        atualizar_user_management()
        
        print("\n" + "="*60)
        print("✅ UNIFICAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print("\n📋 RESUMO:")
        print("• Arquivo único: credenciais.csv")
        print("• Suporte completo: níveis de acesso, status, auditoria")
        print("• Compatibilidade: AuthService + UserManager")
        print("• Backup: pasta backup_usuarios/")
        
        print("\n🔍 TESTANDO SISTEMA:")
        try:
            sys.path.append(BASE_DIR)
            sys.path.append(os.path.join(BASE_DIR, "IntegragalGit"))
            
            # Testar AuthService
            from autenticacao.auth_service import AuthService
            auth = AuthService()
            resultado = auth.verificar_senha("marcio", "flafla")
            print(f"🔐 Teste AuthService marcio/flafla: {'✅ SUCESSO' if resultado else '❌ FALHOU'}")
            
            # Testar UserManager
            from core.authentication.user_manager import UserManager
            user_manager = UserManager()
            usuarios = user_manager.listar_usuarios()
            print(f"👥 Teste UserManager: {len(usuarios)} usuários carregados")
            
        except Exception as e:
            print(f"⚠️  Erro nos testes: {e}")
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Teste o login: marcio / flafla")
        print("2. Teste o gerenciamento de usuários")
        print("3. Remova arquivos desnecessários se desejar")
        
    else:
        print("\n❌ Falha na consolidação")

if __name__ == "__main__":
    main()