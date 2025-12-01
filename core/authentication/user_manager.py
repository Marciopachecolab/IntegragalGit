#!/usr/bin/env python3
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
