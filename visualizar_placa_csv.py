"""
Script para visualizar a placa usando dados de tmp_df_norm_excerpt.csv
Carrega o CSV e abre o visualizador de placas.

Executar: python visualizar_placa_csv.py
"""

import sys
import pandas as pd
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from services.plate_viewer import abrir_placa_ctk
import customtkinter as ctk

def carregar_e_visualizar_placa(csv_path: str = "tmp_df_norm_excerpt.csv"):
    """
    Carrega dados do CSV e abre o visualizador de placas.
    
    Args:
        csv_path: Caminho do arquivo CSV
    """
    print("=" * 100)
    print("VISUALIZADOR DE PLACA - Carregando de CSV")
    print("=" * 100)
    print()
    
    # Verificar se arquivo existe
    csv_file = Path(csv_path)
    if not csv_file.exists():
        print(f"❌ Erro: Arquivo não encontrado: {csv_path}")
        return
    
    print(f"📂 Carregando arquivo: {csv_path}")
    
    try:
        # Carregar CSV com separador ponto-e-vírgula
        df = pd.read_csv(csv_path, sep=";", encoding="utf-8")
        
        print(f"✅ Arquivo carregado com sucesso!")
        print(f"   Shape: {df.shape[0]} linhas x {df.shape[1]} colunas")
        print()
        
        # Converter colunas CT que têm vírgula como separador decimal
        print("🔄 Convertendo valores CT (vírgula → ponto)...")
        ct_columns = [col for col in df.columns if " - CT" in col or "CT" in col.upper()]
        for col in ct_columns:
            if col in df.columns:
                # Substituir vírgula por ponto e converter para float
                df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        if ct_columns:
            print(f"   ✅ {len(ct_columns)} colunas CT convertidas")
        print()
        
        # Mostrar informações do DataFrame
        print("📊 Colunas disponíveis:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2d}. {col}")
        print()
        
        # Verificar colunas essenciais
        colunas_essenciais = ["poco", "amostra", "codigo"]
        colunas_faltantes = [c for c in colunas_essenciais if c not in df.columns]
        
        if colunas_faltantes:
            print(f"⚠️  Colunas essenciais faltantes: {colunas_faltantes}")
            print("   Tentando normalizar nomes de colunas...")
            
            # Tentar mapear colunas com nomes similares
            col_map = {}
            for col in df.columns:
                col_lower = col.lower().strip()
                if "poco" in col_lower or "poço" in col_lower:
                    col_map[col] = "poco"
                elif "amostra" in col_lower or "sample" in col_lower:
                    col_map[col] = "amostra"
                elif "codigo" in col_lower or "código" in col_lower or "code" in col_lower:
                    col_map[col] = "codigo"
            
            if col_map:
                df = df.rename(columns=col_map)
                print(f"   ✅ Colunas renomeadas: {col_map}")
        
        # Mostrar primeiras linhas
        print("📋 Primeiras linhas do DataFrame:")
        print(df.head(3).to_string())
        print()
        
        # Extrair metadata do DataFrame
        metadata = {}
        
        # Tentar extrair informações das colunas de metadata
        if "usuario_analise" in df.columns and len(df) > 0:
            metadata["usuario"] = df["usuario_analise"].iloc[0]
        
        if "exame" in df.columns and len(df) > 0:
            metadata["exame"] = df["exame"].iloc[0]
        
        if "lote" in df.columns and len(df) > 0:
            metadata["lote"] = df["lote"].iloc[0]
        
        if "arquivo_corrida" in df.columns and len(df) > 0:
            metadata["extracao"] = df["arquivo_corrida"].iloc[0]
        
        if "data_hora_analise" in df.columns and len(df) > 0:
            metadata["data"] = df["data_hora_analise"].iloc[0]
        
        print("📝 Metadata extraída:")
        for key, value in metadata.items():
            print(f"   {key}: {value}")
        print()
        
        # Determinar tamanho do grupo baseado no formato do poco
        group_size = 2  # Default
        if len(df) > 0 and "poco" in df.columns:
            primeiro_poco = str(df["poco"].iloc[0])
            if "+" in primeiro_poco:
                group_size = len(primeiro_poco.split("+"))
                print(f"🔢 Tamanho de grupo detectado: {group_size} (baseado em '{primeiro_poco}')")
            print()
        
        # Abrir visualizador de placa
        print("🖥️  Abrindo visualizador de placa...")
        print("=" * 100)
        print()
        
        # Criar janela principal
        root = ctk.CTk()
        root.withdraw()  # Esconder janela principal
        
        # Abrir placa
        abrir_placa_ctk(
            df_final=df,
            meta_extra=metadata,
            group_size=group_size,
            parent=root
        )
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Permitir especificar arquivo como argumento
    import sys
    
    csv_path = "tmp_df_norm_excerpt.csv"
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    
    carregar_e_visualizar_placa(csv_path)
