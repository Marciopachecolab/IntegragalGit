"""
Módulo para gerar relatórios detalhados de DataFrames durante o processamento.
Captura e registra informações de todos os DataFrames principais do sistema.
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json


class DataFrameReporter:
    """
    Gerenciador de relatórios de DataFrames.
    Captura informações detalhadas sobre DataFrames em diferentes etapas do processamento.
    """
    
    def __init__(self, log_dir: str = "logs/dataframe_reports"):
        """
        Inicializa o reporter.
        
        Args:
            log_dir: Diretório onde os relatórios serão salvos
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_session = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.reports = []
        
    def capture_dataframe(
        self,
        df: pd.DataFrame,
        name: str,
        stage: str,
        metadata: Optional[Dict[str, Any]] = None,
        save_sample: bool = True,
        sample_rows: int = 10
    ) -> Dict[str, Any]:
        """
        Captura informações detalhadas de um DataFrame.
        
        Args:
            df: DataFrame a ser analisado
            name: Nome identificador do DataFrame (ex: 'df_resultados', 'df_norm')
            stage: Estágio do processamento (ex: 'extracao', 'analise', 'final')
            metadata: Informações adicionais sobre o contexto
            save_sample: Se True, salva amostra dos dados
            sample_rows: Número de linhas da amostra
            
        Returns:
            Dicionário com informações capturadas
        """
        if df is None:
            report = {
                "timestamp": datetime.now().isoformat(),
                "session": self.current_session,
                "name": name,
                "stage": stage,
                "status": "NULL",
                "metadata": metadata or {}
            }
            self.reports.append(report)
            return report
        
        try:
            # Informações básicas
            report = {
                "timestamp": datetime.now().isoformat(),
                "session": self.current_session,
                "name": name,
                "stage": stage,
                "status": "OK",
                "shape": {"rows": len(df), "cols": len(df.columns)},
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024**2),
                "metadata": metadata or {}
            }
            
            # Estatísticas de valores nulos
            null_counts = df.isnull().sum()
            report["null_counts"] = {
                col: int(count) for col, count in null_counts.items() if count > 0
            }
            
            # Valores únicos para colunas principais
            key_columns = ["Poco", "Amostra", "Codigo", "exame", "poco"]
            report["unique_counts"] = {}
            for col in key_columns:
                if col in df.columns:
                    report["unique_counts"][col] = int(df[col].nunique())
            
            # Salvar amostra dos dados se solicitado
            if save_sample and len(df) > 0:
                sample_file = self.log_dir / f"{self.current_session}_{name}_{stage}_sample.csv"
                df.head(sample_rows).to_csv(sample_file, index=False, encoding="utf-8-sig")
                report["sample_file"] = str(sample_file)
            
            self.reports.append(report)
            return report
            
        except Exception as e:
            report = {
                "timestamp": datetime.now().isoformat(),
                "session": self.current_session,
                "name": name,
                "stage": stage,
                "status": "ERROR",
                "error": str(e),
                "metadata": metadata or {}
            }
            self.reports.append(report)
            return report
    
    def generate_summary_report(self, output_file: Optional[str] = None) -> str:
        """
        Gera relatório resumido de todos os DataFrames capturados.
        
        Args:
            output_file: Caminho do arquivo de saída (opcional)
            
        Returns:
            String com o relatório formatado
        """
        if not self.reports:
            return "Nenhum DataFrame capturado nesta sessão."
        
        lines = []
        lines.append("=" * 100)
        lines.append(f"RELATÓRIO DE DATAFRAMES - Sessão {self.current_session}")
        lines.append("=" * 100)
        lines.append(f"Total de DataFrames capturados: {len(self.reports)}")
        lines.append(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Agrupar por estágio
        stages = {}
        for report in self.reports:
            stage = report.get("stage", "unknown")
            if stage not in stages:
                stages[stage] = []
            stages[stage].append(report)
        
        for stage, stage_reports in stages.items():
            lines.append("")
            lines.append("=" * 100)
            lines.append(f"ESTÁGIO: {stage.upper()}")
            lines.append("=" * 100)
            
            for report in stage_reports:
                lines.append("")
                lines.append(f"  DataFrame: {report['name']}")
                lines.append(f"  Timestamp: {report['timestamp']}")
                lines.append(f"  Status: {report['status']}")
                
                if report['status'] == 'NULL':
                    lines.append("  ⚠️  DataFrame é None/NULL")
                    
                elif report['status'] == 'ERROR':
                    lines.append(f"  ❌ Erro: {report.get('error', 'Desconhecido')}")
                    
                elif report['status'] == 'OK':
                    shape = report.get('shape', {})
                    lines.append(f"  Shape: {shape.get('rows', 0)} linhas x {shape.get('cols', 0)} colunas")
                    lines.append(f"  Memória: {report.get('memory_usage_mb', 0):.2f} MB")
                    
                    # Colunas
                    cols = report.get('columns', [])
                    if len(cols) <= 10:
                        lines.append(f"  Colunas: {', '.join(cols)}")
                    else:
                        lines.append(f"  Colunas ({len(cols)}): {', '.join(cols[:5])} ... {', '.join(cols[-3:])}")
                    
                    # Valores nulos
                    null_counts = report.get('null_counts', {})
                    if null_counts:
                        lines.append(f"  Valores nulos: {len(null_counts)} colunas com dados faltantes")
                        for col, count in list(null_counts.items())[:5]:
                            lines.append(f"    - {col}: {count} nulos")
                    else:
                        lines.append("  ✅ Sem valores nulos")
                    
                    # Valores únicos
                    unique_counts = report.get('unique_counts', {})
                    if unique_counts:
                        lines.append(f"  Valores únicos:")
                        for col, count in unique_counts.items():
                            lines.append(f"    - {col}: {count} únicos")
                    
                    # Arquivo de amostra
                    sample_file = report.get('sample_file')
                    if sample_file:
                        lines.append(f"  📄 Amostra salva: {sample_file}")
                
                # Metadata
                metadata = report.get('metadata', {})
                if metadata:
                    lines.append("  Metadata:")
                    for key, value in metadata.items():
                        lines.append(f"    - {key}: {value}")
                
                lines.append("  " + "-" * 96)
        
        # Estatísticas gerais
        lines.append("")
        lines.append("=" * 100)
        lines.append("ESTATÍSTICAS GERAIS")
        lines.append("=" * 100)
        
        total_ok = sum(1 for r in self.reports if r['status'] == 'OK')
        total_null = sum(1 for r in self.reports if r['status'] == 'NULL')
        total_error = sum(1 for r in self.reports if r['status'] == 'ERROR')
        
        lines.append(f"  DataFrames OK: {total_ok}")
        lines.append(f"  DataFrames NULL: {total_null}")
        lines.append(f"  DataFrames com Erro: {total_error}")
        
        if total_ok > 0:
            total_rows = sum(r.get('shape', {}).get('rows', 0) for r in self.reports if r['status'] == 'OK')
            total_memory = sum(r.get('memory_usage_mb', 0) for r in self.reports if r['status'] == 'OK')
            lines.append(f"  Total de linhas processadas: {total_rows:,}")
            lines.append(f"  Uso total de memória: {total_memory:.2f} MB")
        
        lines.append("")
        lines.append("=" * 100)
        
        report_text = "\n".join(lines)
        
        # Salvar em arquivo se especificado
        if output_file:
            Path(output_file).write_text(report_text, encoding="utf-8")
        else:
            # Salvar no diretório de logs com nome automático
            default_file = self.log_dir / f"{self.current_session}_summary.txt"
            default_file.write_text(report_text, encoding="utf-8")
            lines.append(f"\n📊 Relatório salvo em: {default_file}")
        
        return report_text
    
    def export_json(self, output_file: Optional[str] = None) -> str:
        """
        Exporta todos os relatórios em formato JSON.
        
        Args:
            output_file: Caminho do arquivo de saída (opcional)
            
        Returns:
            Caminho do arquivo JSON gerado
        """
        if not output_file:
            output_file = self.log_dir / f"{self.current_session}_reports.json"
        
        output_path = Path(output_file)
        
        export_data = {
            "session": self.current_session,
            "generated_at": datetime.now().isoformat(),
            "total_reports": len(self.reports),
            "reports": self.reports
        }
        
        output_path.write_text(
            json.dumps(export_data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        return str(output_path)


# Instância global do reporter
_global_reporter: Optional[DataFrameReporter] = None


def get_reporter() -> DataFrameReporter:
    """Retorna a instância global do reporter (cria se não existir)."""
    global _global_reporter
    if _global_reporter is None:
        _global_reporter = DataFrameReporter()
    return _global_reporter


def reset_reporter():
    """Reseta a instância global do reporter."""
    global _global_reporter
    _global_reporter = None


def log_dataframe(
    df: pd.DataFrame,
    name: str,
    stage: str,
    metadata: Optional[Dict[str, Any]] = None,
    save_sample: bool = True
):
    """
    Função de conveniência para registrar um DataFrame.
    
    Args:
        df: DataFrame a ser registrado
        name: Nome do DataFrame
        stage: Estágio do processamento
        metadata: Informações adicionais
        save_sample: Se deve salvar amostra
    """
    reporter = get_reporter()
    return reporter.capture_dataframe(df, name, stage, metadata, save_sample)


def generate_report(output_file: Optional[str] = None) -> str:
    """
    Gera relatório resumido.
    
    Args:
        output_file: Arquivo de saída (opcional)
        
    Returns:
        Texto do relatório
    """
    reporter = get_reporter()
    return reporter.generate_summary_report(output_file)
