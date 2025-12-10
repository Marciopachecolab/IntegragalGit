"""
Sistema de Gerenciamento de Configurações do IntegRAGal

⚠️ DEPRECATED: Este módulo está sendo migrado para usar ConfigService.
   Para novo código, use diretamente:
   
   from services.config_service import config_service
   
Este módulo agora atua como um ADAPTER para compatibilidade com código existente.
Todas as operações são redirecionadas para ConfigService.

ARQUITETURA (FASE 3 - R9):
  ✅ Fonte de verdade: services/config_service.py
  🔄 Adapter (compatibilidade): config/settings.py (este arquivo)
  ❌ Deprecado: Leituras diretas de config.json

Ver: RELATORIO_REDUNDANCIA_CONFLITOS.md (FASE 3, Etapa 3.3)
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime
import shutil
import warnings

from utils.logger import registrar_log
from utils.validator import Validator
from utils.error_handler import ErrorHandler, safe_operation

# Import do ConfigService (fonte de verdade única)
from services.config_service import config_service as _config_service


class ConfigurationManager:
    """Gerenciador centralizado de configurações do sistema"""
    
    # Caminhos dos arquivos de configuração
    DEFAULT_CONFIG_PATH = Path("config/default_config.json")
    USER_CONFIG_PATH = Path("config/user_config.json")
    BACKUP_DIR = Path("config/backups")
    
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        """Implementa padrão Singleton"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa o gerenciador de configurações"""
        if self._initialized:
            return
            
        self.config: Dict[str, Any] = {}
        self.default_config: Dict[str, Any] = {}
        self._observers = []  # Para notificar mudanças
        
        # Carrega configurações
        self._carregar_configuracoes()
        self._initialized = True
    
    @safe_operation(fallback_value={}, context="Carregando configurações padrão")
    def _carregar_configuracoes_padrao(self) -> Dict[str, Any]:
        """Carrega configurações padrão do arquivo JSON"""
        if not Validator.arquivo_existe(self.DEFAULT_CONFIG_PATH):
            ErrorHandler.show_warning(
                "Configuração Padrão Não Encontrada",
                f"Arquivo {self.DEFAULT_CONFIG_PATH} não encontrado",
                "O sistema usará configurações internas"
            )
            return self._obter_configuracoes_hardcoded()
        
        with open(self.DEFAULT_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        registrar_log(
            "Configuração",
            f"Configurações padrão carregadas de {self.DEFAULT_CONFIG_PATH}",
            "INFO"
        )
        return config
    
    @safe_operation(fallback_value={}, context="Carregando configurações do usuário")
    def _carregar_configuracoes_usuario(self) -> Dict[str, Any]:
        """Carrega configurações personalizadas do usuário"""
        if not Validator.arquivo_existe(self.USER_CONFIG_PATH):
            return {}  # Sem configurações personalizadas ainda
        
        with open(self.USER_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        registrar_log(
            "Configuração",
            f"Configurações do usuário carregadas de {self.USER_CONFIG_PATH}",
            "INFO"
        )
        return config
    
    def _carregar_configuracoes(self):
        """Carrega e mescla configurações padrão e do usuário"""
        # Carrega configurações padrão
        self.default_config = self._carregar_configuracoes_padrao()
        
        # Carrega configurações do usuário
        user_config = self._carregar_configuracoes_usuario()
        
        # Mescla (user_config sobrescreve default_config)
        self.config = self._mesclar_configuracoes(self.default_config, user_config)
    
    def _mesclar_configuracoes(self, base: Dict, override: Dict) -> Dict:
        """Mescla duas configurações, com override tendo precedência"""
        resultado = base.copy()
        
        for key, value in override.items():
            if key in resultado and isinstance(resultado[key], dict) and isinstance(value, dict):
                # Recursivamente mescla dicionários aninhados
                resultado[key] = self._mesclar_configuracoes(resultado[key], value)
            else:
                resultado[key] = value
        
        return resultado
    
    @safe_operation(fallback_value=True, context="Salvando configurações")
    def salvar(self, fazer_backup: bool = True) -> bool:
        """
        Salva configurações atuais do usuário
        
        Args:
            fazer_backup: Se True, cria backup antes de salvar
            
        Returns:
            True se sucesso, False caso contrário
        """
        # Cria diretório se não existir
        self.USER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup das configurações atuais
        if fazer_backup and Validator.arquivo_existe(self.USER_CONFIG_PATH):
            self._criar_backup()
        
        # Salva apenas as diferenças em relação ao padrão
        user_config = self._extrair_diferencas(self.default_config, self.config)
        
        # Valida antes de salvar
        if not self._validar_configuracao(user_config):
            ErrorHandler.show_error(
                "Configuração Inválida",
                "As configurações contêm valores inválidos",
                suggestion="Verifique os valores e tente novamente"
            )
            return False
        
        # Salva no arquivo
        with open(self.USER_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(user_config, f, indent=2, ensure_ascii=False)
        
        registrar_log(
            "Configuração",
            f"Configurações do usuário salvas em {self.USER_CONFIG_PATH}",
            "INFO"
        )
        
        # Notifica observadores
        self._notificar_mudancas()
        
        return True
    
    def _extrair_diferencas(self, base: Dict, atual: Dict) -> Dict:
        """Extrai apenas as diferenças entre configuração base e atual"""
        diferencas = {}
        
        for key, value in atual.items():
            if key not in base:
                diferencas[key] = value
            elif isinstance(value, dict) and isinstance(base[key], dict):
                nested_diffs = self._extrair_diferencas(base[key], value)
                if nested_diffs:
                    diferencas[key] = nested_diffs
            elif value != base[key]:
                diferencas[key] = value
        
        return diferencas
    
    @safe_operation(fallback_value=True, context="Criando backup")
    def _criar_backup(self) -> bool:
        """Cria backup das configurações atuais"""
        self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.BACKUP_DIR / f"user_config_backup_{timestamp}.json"
        
        shutil.copy2(self.USER_CONFIG_PATH, backup_path)
        
        registrar_log(
            "Configuração",
            f"Backup criado em {backup_path}",
            "INFO"
        )
        
        # Limpa backups antigos (mantém últimos 10)
        self._limpar_backups_antigos(max_backups=10)
        
        return True
    
    def _limpar_backups_antigos(self, max_backups: int = 10):
        """Remove backups antigos mantendo apenas os mais recentes"""
        if not self.BACKUP_DIR.exists():
            return
        
        backups = sorted(
            self.BACKUP_DIR.glob("user_config_backup_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        # Remove backups excedentes
        for backup in backups[max_backups:]:
            backup.unlink()
    
    def _validar_configuracao(self, config: Dict) -> bool:
        """Valida configuração antes de salvar"""
        # Validações básicas
        if not isinstance(config, dict):
            return False
        
        # Valida seções específicas
        if "aparencia" in config:
            if "tamanho_fonte" in config["aparencia"]:
                if not Validator.numero_valido(
                    config["aparencia"]["tamanho_fonte"], 
                    min_val=8, 
                    max_val=24
                ):
                    return False
        
        if "alertas" in config:
            if "limites_ct" in config["alertas"]:
                ct_alto = config["alertas"]["limites_ct"].get("ct_alto_limite")
                ct_baixo = config["alertas"]["limites_ct"].get("ct_baixo_limite")
                
                if ct_alto is not None and not Validator.ct_valido(ct_alto):
                    return False
                if ct_baixo is not None and not Validator.ct_valido(ct_baixo):
                    return False
        
        return True
    
    def get(self, chave: str, padrao: Any = None) -> Any:
        """
        Obtém valor de configuração usando notação de ponto
        
        Exemplos:
            get("aparencia.tema")
            get("alertas.limites_ct.ct_alto_limite")
        """
        partes = chave.split('.')
        valor = self.config
        
        for parte in partes:
            if isinstance(valor, dict) and parte in valor:
                valor = valor[parte]
            else:
                return padrao
        
        return valor
    
    def set(self, chave: str, valor: Any, salvar_agora: bool = True):
        """
        Define valor de configuração usando notação de ponto
        
        Args:
            chave: Caminho da configuração (ex: "aparencia.tema")
            valor: Novo valor
            salvar_agora: Se True, salva imediatamente no arquivo
        """
        partes = chave.split('.')
        config_ref = self.config
        
        # Navega até o penúltimo nível
        for parte in partes[:-1]:
            if parte not in config_ref:
                config_ref[parte] = {}
            config_ref = config_ref[parte]
        
        # Define o valor
        config_ref[partes[-1]] = valor
        
        # Salva se solicitado
        if salvar_agora:
            self.salvar()
    
    def reset(self, secao: Optional[str] = None):
        """
        Reseta configurações para valores padrão
        
        Args:
            secao: Se especificado, reseta apenas esta seção
        """
        if secao is None:
            # Reseta tudo
            self.config = self.default_config.copy()
        else:
            # Reseta apenas a seção especificada
            if secao in self.default_config:
                self.config[secao] = self.default_config[secao].copy()
        
        self.salvar()
        
        registrar_log(
            "Configuração",
            f"Configurações resetadas: {secao or 'todas'}",
            "INFO"
        )
    
    def adicionar_observer(self, callback):
        """Adiciona observer para ser notificado de mudanças"""
        if callback not in self._observers:
            self._observers.append(callback)
    
    def remover_observer(self, callback):
        """Remove observer"""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def _notificar_mudancas(self):
        """Notifica todos os observers sobre mudanças"""
        for observer in self._observers:
            try:
                observer(self.config)
            except Exception as e:
                registrar_log(
                    "Configuração",
                    f"Erro ao notificar observer: {str(e)}",
                    "ERROR"
                )
    
    def _obter_configuracoes_hardcoded(self) -> Dict[str, Any]:
        """Retorna configurações mínimas hardcoded como fallback"""
        return {
            "aparencia": {
                "tema": "dark",
                "cor_tema": "blue",
                "tamanho_fonte": 13
            },
            "alertas": {
                "habilitar_alertas": True,
                "limites_ct": {
                    "ct_alto_limite": 35.0,
                    "ct_baixo_limite": 15.0
                }
            },
            "exportacao": {
                "formato_padrao": "pdf",
                "diretorio_padrao": "reports"
            }
        }
    
    def exportar_configuracoes(self, caminho: Path) -> bool:
        """Exporta configurações atuais para arquivo"""
        try:
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            registrar_log(
                "Configuração",
                f"Configurações exportadas para {caminho}",
                "INFO"
            )
            return True
        except Exception as e:
            ErrorHandler.handle_exception(
                e,
                context="exportar configurações",
                show_dialog=True
            )
            return False
    
    def importar_configuracoes(self, caminho: Path) -> bool:
        """Importa configurações de arquivo"""
        try:
            if not Validator.arquivo_existe(caminho):
                raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
            
            with open(caminho, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            if not self._validar_configuracao(imported_config):
                raise ValueError("Configuração importada é inválida")
            
            # Mescla com configurações atuais
            self.config = self._mesclar_configuracoes(self.config, imported_config)
            self.salvar()
            
            registrar_log(
                "Configuração",
                f"Configurações importadas de {caminho}",
                "INFO"
            )
            
            ErrorHandler.show_info(
                "Configurações Importadas",
                "As configurações foram importadas com sucesso!"
            )
            return True
            
        except Exception as e:
            ErrorHandler.handle_exception(
                e,
                context="importar configurações",
                show_dialog=True
            )
            return False
    
    def obter_info_configuracoes(self) -> Dict[str, Any]:
        """Retorna informações sobre as configurações atuais"""
        return {
            "total_secoes": len(self.config),
            "secoes": list(self.config.keys()),
            "arquivo_usuario": str(self.USER_CONFIG_PATH),
            "existe_arquivo_usuario": Validator.arquivo_existe(self.USER_CONFIG_PATH),
            "total_backups": len(list(self.BACKUP_DIR.glob("*.json"))) if self.BACKUP_DIR.exists() else 0,
            "versao": self.get("_versao", "1.0.0")
        }


# Instância global singleton
configuracao = ConfigurationManager()


# Funções de conveniência (DEPRECATED - usar ConfigService)
def get_config(chave: str, padrao: Any = None) -> Any:
    """
    Função de conveniência para obter configuração
    
    ⚠️ DEPRECATED: Use config_service.get() diretamente:
        from services.config_service import config_service
        valor = config_service.get('chave')
    """
    warnings.warn(
        "get_config() está deprecated. Use 'from services.config_service import config_service; config_service.get()'",
        DeprecationWarning,
        stacklevel=2
    )
    # Redireciona para ConfigService
    return _config_service.get(chave, padrao)


def set_config(chave: str, valor: Any, salvar: bool = True):
    """
    Função de conveniência para definir configuração
    
    ⚠️ DEPRECATED: Use config_service.set() diretamente:
        from services.config_service import config_service
        config_service.set('chave', valor)
    """
    warnings.warn(
        "set_config() está deprecated. Use 'from services.config_service import config_service; config_service.set()'",
        DeprecationWarning,
        stacklevel=2
    )
    # Redireciona para ConfigService
    _config_service.set(chave, valor)
    if salvar:
        _config_service.save()


def reset_config(secao: Optional[str] = None):
    """
    Função de conveniência para resetar configurações
    
    ⚠️ DEPRECATED: Funcionalidade será movida para ConfigService
    """
    warnings.warn(
        "reset_config() está deprecated.",
        DeprecationWarning,
        stacklevel=2
    )
    configuracao.reset(secao)


def salvar_config() -> bool:
    """
    Função de conveniência para salvar configurações
    
    ⚠️ DEPRECATED: Use config_service.save():
        from services.config_service import config_service
        config_service.save()
    """
    warnings.warn(
        "salvar_config() está deprecated. Use 'config_service.save()'",
        DeprecationWarning,
        stacklevel=2
    )
    return _config_service.save()
