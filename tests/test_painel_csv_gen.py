import pandas as pd
import os

from main import gerar_painel_csvs

# Cria DataFrame de exemplo com resultados
records = [
    {
        "Poco": "A01", "Amostra": "S1", "Codigo": "123",
        "Resultado_INFA": "Detectado", "INFA": 22.5,
        "Resultado_INFB": "ND", "INFB": "",
        "Resultado_SC2": "ND", "SC2": "",
    },
    {
        "Poco": "A02", "Amostra": "S2", "Codigo": "456",
        "Resultado_INFA": "Inc", "INFA": 39.2,
        "Resultado_INFB": "Detectado", "INFB": 21.0,
        "Resultado_SC2": "Detectado", "SC2": 20.1,
    },
]

df_input = pd.DataFrame(records)

print("=" * 80)
print("TESTE DE GERAÇÃO DE PAINEL CSV")
print("=" * 80)

print("\nDataFrame de entrada:")
print(df_input.to_string(index=False))

print("\n" + "-" * 80)
print("Executando gerar_painel_csvs()...")
print("-" * 80)

# Gera painel CSV
result = gerar_painel_csvs(df_input, exame="vr1e2_biomanguinhos_7500", output_dir="./reports")

print(f"\nPainéis gerados: {list(result.keys())}")
for panel_id, path in result.items():
    print(f"  Painel {panel_id}: {path}")
    if os.path.exists(path):
        print(f"    ✓ Arquivo criado ({os.path.getsize(path)} bytes)")
        
        # Lê e valida conteúdo
        df_painel = pd.read_csv(path, sep=";")
        print(f"    Linhas: {len(df_painel)}, Colunas: {len(df_painel.columns)}")
        print(f"    Colunas: {list(df_painel.columns)[:10]}...")  # primeiras 10
        
        # Verifica se há alvos de resultado
        analito_cols = [c for c in df_painel.columns if c not in 
                       ["codigoAmostra", "codigo", "requisicao", "paciente", "exame", "metodo", 
                        "registroInterno", "kit", "reteste", "loteKit", "dataProcessamentoFim", 
                        "valorReferencia", "observacao", "resultado", "painel"]]
        print(f"    Analitos/alvos: {analito_cols}")
        
        # Mostra amostra de dados
        print("\n    Amostra de dados:")
        print(df_painel[["codigo", "exame", "painel"] + analito_cols[:3]].to_string(index=False))
    else:
        print("    ✗ Arquivo não criado!")

print("\n" + "=" * 80)
print("VALIDAÇÃO:")
print("=" * 80)

for panel_id, path in result.items():
    if os.path.exists(path):
        df_painel = pd.read_csv(path, sep=";")
        has_analitos = any(col not in 
                          ["codigoAmostra", "codigo", "requisicao", "paciente", "exame", "metodo", 
                           "registroInterno", "kit", "reteste", "loteKit", "dataProcessamentoFim", 
                           "valorReferencia", "observacao", "resultado", "painel"] 
                          for col in df_painel.columns)
        print(f"\n✓ Painel {panel_id}:")
        print("  - Arquivo criado: SIM")
        print(f"  - Tem colunas de analitos: {'SIM' if has_analitos else 'NÃO'}")
        print(f"  - Linhas de dados: {len(df_painel)}")
        if len(df_painel) == len(df_input):
            print("  ✅ TESTE PASSOU: CSV painel gerado com sucesso!")
        else:
            print(f"  ⚠️  Aviso: linhas não correspondem (esperado {len(df_input)}, obtido {len(df_painel)})")
    else:
        print(f"\n✗ Painel {panel_id}: Arquivo não criado - TESTE FALHOU")

print("=" * 80)
