"""
Script de teste/exemplo do sistema de relatórios de DataFrames.
Demonstra como usar o DataFrameReporter para capturar informações.

Executar: python test_dataframe_reporter.py
"""

import sys
import pandas as pd
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from utils.dataframe_reporter import DataFrameReporter, log_dataframe, generate_report, reset_reporter

print("=" * 100)
print("TESTE DO SISTEMA DE RELATÓRIOS DE DATAFRAMES")
print("=" * 100)
print()

# Resetar reporter para começar limpo
reset_reporter()

# Criar DataFrames de exemplo simulando o fluxo do sistema
print("📊 Criando DataFrames de exemplo...")
print()

# 1. df_extracao (gabarito)
df_extracao = pd.DataFrame({
    "Poco": ["A1", "A2", "B1", "B2"],
    "Amostra": ["422386149R", "422386150R", "422386151R", "422386152R"],
    "Codigo": ["422386149R", "422386150R", "422386151R", "422386152R"],
})
log_dataframe(
    df_extracao,
    name="df_gabarito_extracao",
    stage="extracao",
    metadata={"source": "arquivo_gabarito.xlsx", "usuario": "marci"}
)
print("✅ df_gabarito_extracao registrado")

# 2. df_resultados (resultados brutos do equipamento)
df_resultados = pd.DataFrame({
    "Well": ["A1", "A1", "A2", "A2", "B1", "B1", "B2", "B2"],
    "Sample": ["422386149R", "422386149R", "422386150R", "422386150R", 
               "422386151R", "422386151R", "422386152R", "422386152R"],
    "Target": ["SC2", "HMPV", "SC2", "HMPV", "SC2", "HMPV", "SC2", "HMPV"],
    "Cq": [25.5, None, None, 28.3, 22.1, None, None, 30.5],
})
log_dataframe(
    df_resultados,
    name="df_resultados",
    stage="leitura_equipamento",
    metadata={"equipamento": "7500", "arquivo": "20250718_VR1.xlsx"}
)
print("✅ df_resultados registrado")

# 3. df_norm (após normalização)
df_norm = pd.DataFrame({
    "Poco": ["A1", "A2", "B1", "B2"],
    "Amostra": ["422386149R", "422386150R", "422386151R", "422386152R"],
    "Codigo": ["422386149R", "422386150R", "422386151R", "422386152R"],
    "Resultado_SC2": ["Detectado", "Nao Detectado", "Detectado", "Nao Detectado"],
    "Resultado_HMPV": ["Nao Detectado", "Detectado", "Nao Detectado", "Detectado"],
    "SC2": [25.5, None, 22.1, None],
    "HMPV": [None, 28.3, None, 30.5],
})
log_dataframe(
    df_norm,
    name="df_norm",
    stage="normalizacao",
    metadata={"exame": "VR1-VR2 BIOM", "alvos": ["SC2", "HMPV"]}
)
print("✅ df_norm registrado")

# 4. df_final (após análise e processamento)
df_final = pd.DataFrame({
    "Poco": ["A1", "A2", "B1", "B2"],
    "Amostra": ["422386149R", "422386150R", "422386151R", "422386152R"],
    "Codigo": ["422386149R", "422386150R", "422386151R", "422386152R"],
    "Resultado_SC2": ["Det", "ND", "Det", "ND"],
    "Resultado_HMPV": ["ND", "Det", "ND", "Det"],
    "SC2 - CT": [25.5, None, 22.1, None],
    "HMPV - CT": [None, 28.3, None, 30.5],
    "Status_Analise": ["Concluído", "Concluído", "Concluído", "Concluído"],
})
log_dataframe(
    df_final,
    name="df_final",
    stage="analise",
    metadata={
        "exame": "VR1-VR2 BIOM",
        "usuario": "marci",
        "lote": "LOTE123",
        "data_corrida": "2025-07-18"
    }
)
print("✅ df_final registrado")

# 5. df_processado (após aplicação de regras)
df_processado = df_final.copy()
df_processado["Laudo"] = ["Positivo para SC2", "Positivo para HMPV", 
                          "Positivo para SC2", "Positivo para HMPV"]
log_dataframe(
    df_processado,
    name="df_processado",
    stage="laudo",
    metadata={"regras_aplicadas": True}
)
print("✅ df_processado registrado")

# 6. df_hist (histórico formatado para CSV)
df_hist = pd.DataFrame({
    "poco": ["A1+A2", "B1+B2"],
    "amostra": ["422386149R", "422386151R"],
    "codigo": ["422386149R", "422386151R"],
    "exame": ["VR1-VR2 BIOM", "VR1-VR2 BIOM"],
    "data": ["2025-07-18", "2025-07-18"],
    "usuario": ["marci", "marci"],
    "SC2 - R": ["SC2 - 1", "SC2 - 1"],
    "SC2 - CT": ["25.5", "22.1"],
    "HMPV - R": ["HMPV - 2", "HMPV - 2"],
    "HMPV - CT": ["", ""],
})
log_dataframe(
    df_hist,
    name="df_hist",
    stage="historico",
    metadata={"destino": "logs/historico_analises.csv", "formato": "agrupado"}
)
print("✅ df_hist registrado")

# 7. Simular DataFrame NULL
log_dataframe(
    None,
    name="df_opcional",
    stage="analise",
    metadata={"motivo": "Dado opcional não disponível"}
)
print("⚠️  df_opcional (NULL) registrado")

print()
print("=" * 100)
print("GERANDO RELATÓRIO FINAL...")
print("=" * 100)
print()

# Gerar relatório resumido
report_text = generate_report()
print(report_text)

print()
print("=" * 100)
print("✅ TESTE CONCLUÍDO COM SUCESSO!")
print("=" * 100)
print()
print("📁 Verifique o diretório 'logs/dataframe_reports/' para:")
print("   - Arquivos CSV com amostras dos dados")
print("   - Relatório resumido em TXT")
print("   - Relatório completo em JSON")
