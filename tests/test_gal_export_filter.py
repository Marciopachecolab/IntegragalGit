import pandas as pd

from main import _formatar_para_gal



# Cria DataFrame de exemplo com vários tipos de código

records = [

    {"Poco": "A01", "Amostra": "S1", "Codigo": "123", "Resultado_INFA": "Detectado", "INFA": 22.5},  # exportável

    {"Poco": "A02", "Amostra": "S2", "Codigo": "456", "Resultado_INFA": "ND", "INFA": ""},  # exportável

    {"Poco": "A03", "Amostra": "CN", "Codigo": "CN", "Resultado_INFA": "ND", "INFA": ""},  # controle negativo - NÃO exportável

    {"Poco": "A04", "Amostra": "CP", "Codigo": "CP", "Resultado_INFA": "Detectado", "INFA": 21.0},  # controle positivo - NÃO exportável

    {"Poco": "A05", "Amostra": "S3", "Codigo": "ABC123", "Resultado_INFA": "Detectado", "INFA": 23.1},  # alfanumérico - NÃO exportável

    {"Poco": "A06", "Amostra": "S4", "Codigo": "789", "Resultado_INFA": "Inc", "INFA": 39.5},  # exportável

]



df_input = pd.DataFrame(records)



print("=" * 80)

print("TESTE DE EXPORTAÇÃO GAL - Filtro de Códigos CN/CP e Não Numéricos")

print("=" * 80)



print("\nDataFrame de entrada (6 registros):")

print(df_input[["Codigo", "Amostra", "Resultado_INFA"]].to_string(index=False))



print("\n" + "-" * 80)

print("Executando _formatar_para_gal()...")

print("-" * 80)



df_output = _formatar_para_gal(df_input, exame="vr1e2_biomanguinhos_7500")



print(f"\nDataFrame de saída (após filtro): {len(df_output)} registros exportáveis")

print(df_output[["codigo", "codigoAmostra"]].to_string(index=False))



print("\n" + "=" * 80)

print("VALIDAÇÃO:")

print("=" * 80)



# Valida que apenas registros com códigos numéricos foram exportados

input_codes = set(df_input["Codigo"].values)

output_codes = set(df_output["codigo"].values)



print(f"\nCódigos na entrada: {sorted(input_codes)}")

print(f"Códigos na saída:   {sorted(output_codes)}")



# Verifica filtros

expected_filtered = {"CN", "CP", "ABC123"}  # Devem ser excluídos

expected_exported = {"123", "456", "789"}    # Devem estar presentes



filtered_correctly = expected_filtered.isdisjoint(output_codes)

exported_correctly = expected_exported.issubset(output_codes)



print(f"\n✓ CN/CP foram excluídos: {filtered_correctly}")

print(f"✓ Códigos alfanuméricos foram excluídos: {'ABC123' not in output_codes}")

print(f"✓ Códigos numéricos foram exportados: {exported_correctly}")



if filtered_correctly and exported_correctly and "ABC123" not in output_codes:

    print("\n✅ TESTE PASSOU: Filtro funcionando corretamente!")

else:

    print("\n❌ TESTE FALHOU: Algo está incorreto no filtro.")



print("=" * 80)

