"""
Teste de integração do Universal Engine com Parser e Rules Engine
"""
import sys
sys.path.insert(0, 'c:\\Users\\marci\\downloads\\integragal')

import pandas as pd
from types import SimpleNamespace
from services.universal_engine import UniversalEngine
from services.config_service import config_service

print("=" * 60)
print("TESTE DE INTEGRAÇÃO - UNIVERSAL ENGINE + RULES")
print("=" * 60)
print()

# Criar dados de teste simulando VR1e2 Biomanguinhos 7500
df_resultados = pd.DataFrame({
    'Well': ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2'],
    'Sample Name': ['Amostra1', 'Amostra1', 'Amostra2', 'Amostra2', 'CIP', 'CIP', 'CNP', 'CNP'],
    'Target Name': ['DEN1', 'DEN1', 'DEN2', 'DEN2', 'IC', 'IC', 'IC', 'IC'],
    'Ct': [15.5, 16.2, 22.3, 23.1, 28.0, 28.5, 29.0, 29.8],
    'Ct Mean': [15.85, 15.85, 22.70, 22.70, 28.25, 28.25, 29.40, 29.40],
    'Ct SD': [0.49, 0.49, 0.57, 0.57, 0.35, 0.35, 0.57, 0.57]
})

print("Dados de entrada (formato VR1e2):")
print(df_resultados)
print()

# Criar engine e processar
cfg = config_service
engine = UniversalEngine(cfg)

try:
    print("Processando exame VR1e2 Biomanguinhos 7500...")
    # Usando exame real do sistema
    resultado = engine.processar_exame(
        exame='VR1e2 Biomanguinhos 7500',
        df_resultados=df_resultados,
        lote='TESTE001'
    )
    
    print("\n" + "=" * 60)
    print("RESULTADO DO PROCESSAMENTO")
    print("=" * 60)
    
    print(f"\n✅ Status da corrida: {resultado.resumo.get('status_corrida', 'N/A')}")
    print(f"✅ Lote: {resultado.resumo.get('lote', 'N/A')}")
    
    print(f"\nMetadados:")
    for key, value in resultado.metadados.items():
        if key.startswith('regras_'):
            print(f"  {key}: {value}")
    
    if hasattr(resultado, 'regras_resultado') and resultado.regras_resultado:
        print(f"\n📊 RESULTADO DAS REGRAS:")
        rr = resultado.regras_resultado
        print(f"  Status: {rr.status}")
        print(f"  Detalhes: {rr.detalhes}")
        print(f"  Tempo: {rr.tempo_execucao_ms:.2f}ms")
        
        if rr.validacoes:
            print(f"\n  Validações ({len(rr.validacoes)}):")
            for v in rr.validacoes:
                icon = "✅" if v.resultado == "passou" else "❌" if v.resultado == "falhou" else "⚠️"
                print(f"    {icon} {v.regra_nome}: {v.resultado}")
                print(f"       {v.detalhes}")
        
        if rr.mensagens_erro:
            print(f"\n  ❌ Erros:")
            for err in rr.mensagens_erro:
                print(f"    - {err}")
        
        if rr.mensagens_aviso:
            print(f"\n  ⚠️  Avisos:")
            for aviso in rr.mensagens_aviso:
                print(f"    - {aviso}")
    else:
        print(f"\n📊 Nenhuma regra foi aplicada (não configuradas para este exame)")
    
    print(f"\nDataFrame final:")
    print(resultado.df_final)
    
    print("\n" + "=" * 60)
    print("✅ INTEGRAÇÃO FUNCIONANDO!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("TESTE CONCLUÍDO")
print("=" * 60)
