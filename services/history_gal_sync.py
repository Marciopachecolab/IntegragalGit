#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
services/history_gal_sync.py

Módulo para sincronizar status de envio GAL com o histórico CSV.
Fornece funções para:
- Atualizar status após envio bem-sucedido
- Registrar falhas de envio
- Consultar estado de registros
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

import pandas as pd

# Garante que o diretório raiz está no path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from utils.logger import registrar_log


class HistoricoGALSync:
    """
    Gerenciador de sincronização entre análises e envio GAL.
    Atualiza histórico CSV com status de envio.
    """
    
    def __init__(self, csv_path: str = "logs/historico_analises.csv"):
        """
        Inicializa o sincronizador.
        
        Args:
            csv_path: Caminho do arquivo histórico
        """
        self.csv_path = Path(csv_path)
        self._valida_arquivo()
    
    def _valida_arquivo(self) -> None:
        """Valida se arquivo existe e tem estrutura correta."""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.csv_path}")
        
        try:
            df = pd.read_csv(self.csv_path, sep=";", encoding="utf-8", nrows=1)
            
            campos_obrigatorios = [
                "id_registro",
                "status_gal",
                "data_hora_envio",
                "usuario_envio",
                "sucesso_envio",
                "detalhes_envio",
                "atualizado_em"
            ]
            
            campos_faltando = [c for c in campos_obrigatorios if c not in df.columns]
            if campos_faltando:
                raise ValueError(
                    f"Campos faltando no CSV: {campos_faltando}. "
                    f"Execute migração primeiro: scripts/migrate_historical_csv.py"
                )
        except Exception as e:
            raise ValueError(f"Erro ao validar CSV: {e}")
    
    def marcar_enviado(
        self,
        id_registros: List[str],
        usuario_envio: str,
        detalhes: str = "Enviado com sucesso para GAL"
    ) -> Dict[str, Any]:
        """
        Marca registros como enviados com sucesso.
        
        Args:
            id_registros: Lista de IDs (UUIDs) dos registros
            usuario_envio: Quem fez o envio
            detalhes: Mensagem descritiva
        
        Returns:
            Dict com estatísticas da atualização
        """
        
        return self._atualizar_registros(
            id_registros=id_registros,
            status_gal="enviado",
            sucesso=True,
            usuario_envio=usuario_envio,
            detalhes=detalhes
        )
    
    def marcar_falha_envio(
        self,
        id_registros: List[str],
        usuario_envio: str,
        erro: str
    ) -> Dict[str, Any]:
        """
        Marca registros como falha no envio.
        
        Args:
            id_registros: Lista de IDs (UUIDs) dos registros
            usuario_envio: Quem tentou fazer o envio
            erro: Mensagem de erro do servidor/sistema
        
        Returns:
            Dict com estatísticas da atualização
        """
        
        return self._atualizar_registros(
            id_registros=id_registros,
            status_gal="falha no envio",
            sucesso=False,
            usuario_envio=usuario_envio,
            detalhes=f"Erro: {erro}"
        )
    
    def _atualizar_registros(
        self,
        id_registros: List[str],
        status_gal: str,
        sucesso: bool,
        usuario_envio: str,
        detalhes: str
    ) -> Dict[str, Any]:
        """
        Atualiza registros no CSV com informações de envio.
        
        Args:
            id_registros: Lista de IDs
            status_gal: Novo status
            sucesso: True/False para resultado
            usuario_envio: Quem fez o envio
            detalhes: Detalhes do envio/erro
        
        Returns:
            Estatísticas da atualização
        """
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # 1. Lê o CSV completo
            df = pd.read_csv(self.csv_path, sep=";", encoding="utf-8")
            
            registros_atualizados = 0
            registros_nao_encontrados = []
            
            # 2. Para cada ID fornecido
            for id_reg in id_registros:
                mask = df["id_registro"] == id_reg
                
                if not mask.any():
                    registros_nao_encontrados.append(id_reg)
                    continue
                
                # 3. Atualiza campos de envio
                df.loc[mask, "status_gal"] = status_gal
                df.loc[mask, "data_hora_envio"] = timestamp
                df.loc[mask, "usuario_envio"] = usuario_envio
                df.loc[mask, "sucesso_envio"] = sucesso
                df.loc[mask, "detalhes_envio"] = detalhes
                df.loc[mask, "atualizado_em"] = timestamp
                
                registros_atualizados += 1
            
            # 4. Escreve de volta (sobrescreve)
            df.to_csv(self.csv_path, sep=";", index=False, encoding="utf-8")
            
            # 5. Prepara resposta
            resultado = {
                "sucesso": True,
                "registros_atualizados": registros_atualizados,
                "registros_nao_encontrados": registros_nao_encontrados,
                "timestamp": timestamp,
                "status": status_gal,
                "usuario": usuario_envio
            }
            
            # Log
            mensagem = (
                f"Atualizado histórico: {registros_atualizados} registros com status "
                f"'{status_gal}', enviados por {usuario_envio}"
            )
            if registros_nao_encontrados:
                mensagem += f" ({len(registros_nao_encontrados)} não encontrados)"
            
            registrar_log("Histórico GAL Sync", mensagem, "INFO")
            
            return resultado
        
        except Exception as e:
            mensagem = f"Erro ao atualizar registros: {e}"
            registrar_log("Histórico GAL Sync", mensagem, "ERROR")
            
            return {
                "sucesso": False,
                "erro": str(e),
                "registros_atualizados": 0,
                "registros_nao_encontrados": id_registros
            }
    
    def obter_nao_enviados(
        self,
        exame: Optional[str] = None,
        limite: int = 100
    ) -> pd.DataFrame:
        """
        Obtém registros que ainda não foram enviados para GAL.
        
        Args:
            exame: Filtrar por exame (opcional)
            limite: Máximo de registros a retornar
        
        Returns:
            DataFrame com registros não enviados
        """
        
        try:
            df = pd.read_csv(self.csv_path, sep=";", encoding="utf-8")
            
            # Filtra por status
            mask = df["status_gal"] == "não enviado"
            
            # Filtra por exame se especificado
            if exame:
                mask = mask & (df["exame"] == exame)
            
            resultado = df[mask].head(limite)
            
            return resultado
        
        except Exception as e:
            registrar_log(
                "Histórico GAL Sync",
                f"Erro ao obter não enviados: {e}",
                "ERROR"
            )
            return pd.DataFrame()
    
    def obter_por_id(self, id_registro: str) -> Optional[Dict[str, Any]]:
        """
        Obtém detalhes de um registro pelo ID.
        
        Args:
            id_registro: UUID do registro
        
        Returns:
            Dict com dados do registro ou None se não encontrado
        """
        
        try:
            df = pd.read_csv(self.csv_path, sep=";", encoding="utf-8")
            
            mask = df["id_registro"] == id_registro
            if not mask.any():
                return None
            
            linha = df[mask].iloc[0]
            return linha.to_dict()
        
        except Exception as e:
            registrar_log(
                "Histórico GAL Sync",
                f"Erro ao obter registro {id_registro}: {e}",
                "ERROR"
            )
            return None
    
    def obter_status_lote(self, ids: List[str]) -> Dict[str, Any]:
        """
        Obtém resumo de status para múltiplos registros.
        
        Args:
            ids: Lista de IDs
        
        Returns:
            Dict com contagem por status
        """
        
        try:
            df = pd.read_csv(self.csv_path, sep=";", encoding="utf-8")
            
            df_filtro = df[df["id_registro"].isin(ids)]
            
            resultado = {
                "total": len(df_filtro),
                "não enviado": (df_filtro["status_gal"] == "não enviado").sum(),
                "não enviável": (df_filtro["status_gal"] == "não enviável").sum(),
                "enviado": (df_filtro["status_gal"] == "enviado").sum(),
                "falha no envio": (df_filtro["status_gal"] == "falha no envio").sum(),
                "registros": df_filtro[["id_registro", "status_gal", "codigo", "amostra"]].to_dict(orient="records")
            }
            
            return resultado
        
        except Exception as e:
            registrar_log(
                "Histórico GAL Sync",
                f"Erro ao obter status do lote: {e}",
                "ERROR"
            )
            return {"total": 0, "erro": str(e)}
    
    def reabrir_para_envio(
        self,
        id_registros: List[str]
    ) -> Dict[str, Any]:
        """
        Reabre registros que falharam, para tentar enviar novamente.
        
        Args:
            id_registros: Lista de IDs que falharam
        
        Returns:
            Estatísticas
        """
        
        return self._atualizar_registros(
            id_registros=id_registros,
            status_gal="não enviado",
            sucesso=None,  # Volta ao estado inicial
            usuario_envio="",
            detalhes="Reabertura para retentativa"
        )


# Instância global para facilitar uso
_sync = None


def get_gal_sync(csv_path: str = "logs/historico_analises.csv") -> HistoricoGALSync:
    """Factory para obter instância do sincronizador (singleton)."""
    global _sync
    if _sync is None:
        _sync = HistoricoGALSync(csv_path)
    return _sync


# Funções de conveniência
def marcar_enviados(
    id_registros: List[str],
    usuario: str,
    csv_path: str = "logs/historico_analises.csv"
) -> Dict[str, Any]:
    """
    Marca um lote de registros como enviados com sucesso.
    
    Args:
        id_registros: Lista de UUIDs
        usuario: Quem fez o envio
        csv_path: Caminho do histórico
    
    Returns:
        Resultado da operação
    """
    sync = get_gal_sync(csv_path)
    return sync.marcar_enviado(
        id_registros=id_registros,
        usuario_envio=usuario,
        detalhes="Enviado com sucesso para GAL"
    )


def marcar_falha(
    id_registros: List[str],
    usuario: str,
    erro: str,
    csv_path: str = "logs/historico_analises.csv"
) -> Dict[str, Any]:
    """
    Marca um lote de registros como falha no envio.
    
    Args:
        id_registros: Lista de UUIDs
        usuario: Quem tentou fazer o envio
        erro: Mensagem de erro
        csv_path: Caminho do histórico
    
    Returns:
        Resultado da operação
    """
    sync = get_gal_sync(csv_path)
    return sync.marcar_falha_envio(
        id_registros=id_registros,
        usuario_envio=usuario,
        erro=erro
    )


if __name__ == "__main__":
    # Exemplo de uso
    sync = HistoricoGALSync()
    
    # Obtém registros não enviados
    df_nao_enviados = sync.obter_nao_enviados(limite=10)
    print(f"Registros não enviados: {len(df_nao_enviados)}")
    print(df_nao_enviados[["id_registro", "exame", "codigo", "status_gal"]])
