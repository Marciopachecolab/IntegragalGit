"""
Equipment Registry - Fase 1
Gerencia registro de equipamentos e suas configurações.
"""

from __future__ import annotations

import csv
import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, Optional
import unicodedata


logger = logging.getLogger(__name__)


@dataclass
class EquipmentConfig:
    """Configuração de um equipamento de PCR."""
    
    nome: str
    modelo: str
    fabricante: str
    tipo_placa: str  # "96", "384", etc.
    xlsx_estrutura: Dict[str, Any]  # Estrutura do XLSX
    extrator_nome: str  # Nome da função extratora
    formatador_nome: str = "padrao"  # Nome do formatador
    
    def __post_init__(self):
        """Validar configuração após inicialização."""
        if not self.nome:
            raise ValueError("Nome do equipamento é obrigatório")
        
        if not isinstance(self.xlsx_estrutura, dict):
            raise ValueError("xlsx_estrutura deve ser um dicionário")
        
        # Validar campos obrigatórios em xlsx_estrutura
        campos_obrigatorios = ['coluna_well', 'coluna_target', 'coluna_ct', 'linha_inicio']
        for campo in campos_obrigatorios:
            if campo not in self.xlsx_estrutura:
                raise ValueError(f"xlsx_estrutura deve conter o campo '{campo}'")
        
        # Validar linha_inicio
        linha_inicio = self.xlsx_estrutura.get('linha_inicio')
        if not isinstance(linha_inicio, int) or linha_inicio < 1:
            raise ValueError(f"linha_inicio deve ser int >= 1, recebido: {linha_inicio}")


class EquipmentRegistry:
    """Registro de equipamentos de PCR."""
    
    def __init__(self, caminho_csv: Optional[str] = None):
        """
        Inicializa o registry.
        
        Args:
            caminho_csv: Caminho para arquivo CSV de equipamentos
        """
        self.caminho_csv = caminho_csv or "banco/equipamentos.csv"
        self._cache: Dict[str, EquipmentConfig] = {}
        self._carregado = False
    
    def load(self) -> None:
        """
        Carrega equipamentos do arquivo CSV.
        
        Formato do CSV:
            nome, modelo, fabricante, tipo_placa, xlsx_config (JSON), extrator_nome, formatador_nome
        """
        caminho = Path(self.caminho_csv)
        
        if not caminho.exists():
            logger.warning(f"Arquivo de equipamentos não encontrado: {caminho}")
            logger.info("Usando apenas padrões built-in")
            self._carregar_padroes_builtin()
            self._carregado = True
            return
        
        try:
            # Ler CSV com encoding UTF-8 sem BOM
            with open(caminho, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=',')
                
                linhas_validas = 0
                linhas_invalidas = 0
                
                for i, row in enumerate(reader, start=2):  # Linha 2 (após header)
                    try:
                        # Extrair campos
                        nome = row.get('nome', '').strip()
                        modelo = row.get('modelo', '').strip()
                        fabricante = row.get('fabricante', '').strip()
                        tipo_placa = row.get('tipo_placa', '96').strip()
                        xlsx_config_str = row.get('xlsx_config', '{}').strip()
                        extrator_nome = row.get('extrator_nome', 'generico').strip()
                        formatador_nome = row.get('formatador_nome', 'padrao').strip()
                        
                        if not nome:
                            logger.warning(f"Linha {i}: nome vazio, ignorando")
                            linhas_invalidas += 1
                            continue
                        
                        # Parsear JSON da configuração XLSX
                        try:
                            xlsx_estrutura = json.loads(xlsx_config_str)
                        except json.JSONDecodeError as e:
                            logger.warning(f"Linha {i}: JSON inválido em xlsx_config: {e}")
                            linhas_invalidas += 1
                            continue
                        
                        # Criar configuração
                        config = EquipmentConfig(
                            nome=nome,
                            modelo=modelo,
                            fabricante=fabricante,
                            tipo_placa=tipo_placa,
                            xlsx_estrutura=xlsx_estrutura,
                            extrator_nome=extrator_nome,
                            formatador_nome=formatador_nome
                        )
                        
                        # Adicionar ao cache
                        chave = self._normalizar_chave(nome)
                        self._cache[chave] = config
                        linhas_validas += 1
                        
                    except Exception as e:
                        logger.warning(f"Linha {i}: erro ao processar: {e}")
                        linhas_invalidas += 1
                        continue
                
                logger.info(f"Equipamentos carregados: {linhas_validas} válidos, {linhas_invalidas} inválidos")
        
        except Exception as e:
            logger.error(f"Erro ao ler arquivo CSV: {e}")
            raise
        
        # Adicionar padrões built-in (se não foram sobrescritos)
        self._carregar_padroes_builtin()
        
        self._carregado = True
    
    def _carregar_padroes_builtin(self) -> None:
        """Carrega padrões built-in (hardcoded)."""
        padroes_builtin = [
            EquipmentConfig(
                nome="7500",
                modelo="7500 Real-Time PCR System",
                fabricante="Applied Biosystems",
                tipo_placa="96",
                xlsx_estrutura={
                    "coluna_well": 0,
                    "coluna_sample": 1,
                    "coluna_target": 2,
                    "coluna_ct": 3,
                    "linha_inicio": 5,
                    "headers_esperados": ["Well", "Sample Name", "Target", "Cq"]
                },
                extrator_nome="extrair_7500"
            ),
            EquipmentConfig(
                nome="CFX96",
                modelo="CFX96 Touch Real-Time PCR",
                fabricante="Bio-Rad",
                tipo_placa="96",
                xlsx_estrutura={
                    "coluna_well": 0,
                    "coluna_sample": 1,
                    "coluna_target": 4,
                    "coluna_ct": 5,
                    "linha_inicio": 3,
                    "headers_esperados": ["Well", "Content", "Target", "Cq"]
                },
                extrator_nome="extrair_cfx96"
            ),
            EquipmentConfig(
                nome="QuantStudio",
                modelo="QuantStudio Real-Time PCR",
                fabricante="Thermo Fisher",
                tipo_placa="96",
                xlsx_estrutura={
                    "coluna_well": 1,
                    "coluna_sample": 2,
                    "coluna_target": 3,
                    "coluna_ct": 4,
                    "linha_inicio": 8,
                    "headers_esperados": ["Well Position", "Sample Name", "Target Name", "CT"]
                },
                extrator_nome="extrair_quantstudio"
            ),
            EquipmentConfig(
                nome="7500_Extended",
                modelo="7500 Real-Time PCR System (Extended Format)",
                fabricante="Applied Biosystems",
                tipo_placa="96",
                xlsx_estrutura={
                    "coluna_well": 0,  # Coluna A
                    "coluna_sample": 1,  # Coluna B
                    "coluna_target": 2,  # Coluna C - Target Name
                    "coluna_ct": 6,  # Coluna G - Cт (valor real, não Ct Mean)
                    "linha_inicio": 9,  # Linha 9 (após metadados nas linhas 1-7)
                    "headers_esperados": ["Well", "Sample Name", "Target Name", "Cт"],
                    "keywords": ["sds7500", "7500", "Applied Biosystems"],
                    "skip_sheets": ["extração", "extracao", "extraction"]  # Ignorar abas com esses nomes
                },
                extrator_nome="extrair_7500_extended"
            ),
            EquipmentConfig(
                nome="CFX96_Export",
                modelo="CFX96 Touch Real-Time PCR (Export Format)",
                fabricante="Bio-Rad",
                tipo_placa="96",
                xlsx_estrutura={
                    "coluna_well": 0,
                    "coluna_sample": 1,
                    "coluna_target": 4,
                    "coluna_ct": 6,
                    "linha_inicio": 2,
                    "headers_esperados": ["Well", "Sample", "Target", "Cq"]
                },
                extrator_nome="extrair_cfx96_export"
            )
        ]
        
        for config in padroes_builtin:
            chave = self._normalizar_chave(config.nome)
            # Não sobrescrever se já existe no CSV
            if chave not in self._cache:
                self._cache[chave] = config
    
    def get(self, nome: str) -> Optional[EquipmentConfig]:
        """
        Obtém configuração de equipamento por nome.
        
        Args:
            nome: Nome do equipamento
            
        Returns:
            EquipmentConfig ou None se não encontrado
        """
        if not self._carregado:
            self.load()
        
        chave = self._normalizar_chave(nome)
        return self._cache.get(chave)
    
    def registrar_novo(self, config: EquipmentConfig) -> None:
        """
        Registra novo equipamento (apenas em memória).
        
        Args:
            config: Configuração do equipamento
            
        Raises:
            ValueError: Se configuração inválida
        """
        # Validar configuração
        if not isinstance(config, EquipmentConfig):
            raise ValueError("config deve ser instância de EquipmentConfig")
        
        # Adicionar ao cache
        chave = self._normalizar_chave(config.nome)
        self._cache[chave] = config
        
        logger.info(f"Equipamento registrado: {config.nome}")
    
    def listar_todos(self) -> List[EquipmentConfig]:
        """
        Lista todas as configurações carregadas.
        
        Returns:
            Lista de EquipmentConfig
        """
        if not self._carregado:
            self.load()
        
        return list(self._cache.values())
    
    def listar_equipamentos(self) -> List[str]:
        """
        Lista apenas os nomes dos equipamentos disponíveis.
        
        Returns:
            Lista de strings com nomes dos equipamentos
        """
        if not self._carregado:
            self.load()
        
        return sorted([config.nome for config in self._cache.values()])
    
    def _normalizar_chave(self, nome: str) -> str:
        """
        Normaliza nome para usar como chave (case-insensitive, sem acentos).
        
        Args:
            nome: Nome original
            
        Returns:
            Nome normalizado
        """
        # Remover acentos
        sem_acentos = ''.join(
            c for c in unicodedata.normalize('NFD', nome)
            if unicodedata.category(c) != 'Mn'
        )
        
        # Lowercase e remover espaços extras
        normalizado = sem_acentos.lower().strip()
        normalizado = '_'.join(normalizado.split())
        
        return normalizado


# Instância global (singleton)
_registry_instance: Optional[EquipmentRegistry] = None


def get_registry() -> EquipmentRegistry:
    """Obtém instância global do registry."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = EquipmentRegistry()
        _registry_instance.load()
    return _registry_instance


# API pública
__all__ = [
    'EquipmentConfig',
    'EquipmentRegistry',
    'get_registry'
]
