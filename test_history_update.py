#!/usr/bin/env python3
"""
Script de teste para validar as mudanças em history_report.py
"""

import sys
from pathlib import Path

# Adiciona o diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from services.history_report import gerar_historico_csv, atualizar_status_gal
import pandas as pd


def test_uuid_generation():
    """Testa se UUIDs estão sendo gerados"""
    print("\n📝 Test 1: UUID generation")
    print("-" * 60)
    
    # Cria DataFrame de teste simples
    # IMPORTANTE: Use as mesmas MAIÚSCULAS do código original!
    # Veja: codigo = str(r.get("Codigo", ""))
    df_test = pd.DataFrame({
        "Poco": ["1", "2"],
        "Amostra": ["AMO001", "AMO002"],
        "Codigo": ["001", "002"],  # MAIÚSCULA!
        "Status_Corrida": ["sucesso", "sucesso"],
        "Resultado_alvo_EX200": ["1", "2"],
        "CT_alvo_EX200": ["15.5", "22.3"]
    })
    
    csv_path = "logs/test_historico.csv"
    
    try:
        # Gera histórico
        gerar_historico_csv(
            df_final=df_test,
            exame="VR1e2",
            usuario="teste_user",
            lote="LOTE001",
            arquivo_corrida="RUN001",
            caminho_csv=csv_path
        )
        
        # Verifica se foi criado
        if Path(csv_path).exists():
            df = pd.read_csv(csv_path, sep=";", encoding="utf-8")
            
            # Verifica colunas esperadas
            expected_cols = [
                "id_registro", "data_hora_analise", "usuario_analise", "exame",
                "lote", "arquivo_corrida", "poco", "amostra", "codigo",
                "status_corrida", "status_gal", "mensagem_gal",
                "data_hora_envio", "usuario_envio", "sucesso_envio", "detalhes_envio",
                "criado_em", "atualizado_em"
            ]
            
            missing = [col for col in expected_cols if col not in df.columns]
            if missing:
                print(f"❌ FALHA: Colunas faltantes: {missing}")
                return False
            
            # Verifica UUIDs
            uuids = df["id_registro"].unique()
            if len(uuids) == 2 and all(uid for uid in uuids):
                print(f"✅ PASSOU: 2 registros com UUIDs únicos gerados")
                print(f"   UUID1: {uuids[0]}")
                print(f"   UUID2: {uuids[1]}")
            else:
                print(f"❌ FALHA: UUIDs não foram gerados corretamente")
                return False
            
            # Verifica status_gal
            if all(df["status_gal"] == "não enviado"):
                print(f"✅ PASSOU: Status_gal = 'não enviado' para todos")
            else:
                print(f"❌ FALHA: Status_gal incorreto: {df['status_gal'].unique()}")
                return False
            
            return True
        else:
            print(f"❌ FALHA: Arquivo não foi criado")
            return False
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_status_update():
    """Testa atualização de status após envio"""
    print("\n📝 Test 2: Status update after GAL send")
    print("-" * 60)
    
    csv_path = "logs/test_historico.csv"
    
    try:
        # Lê os IDs gerados
        df = pd.read_csv(csv_path, sep=";", encoding="utf-8")
        id_registros = df["id_registro"].tolist()
        
        if not id_registros:
            print(f"❌ FALHA: Nenhum registro encontrado")
            return False
        
        # Simula envio bem-sucedido do primeiro
        resultado = atualizar_status_gal(
            csv_path=csv_path,
            id_registros=[id_registros[0]],
            sucesso=True,
            usuario_envio="admin",
            detalhes="Enviado com sucesso"
        )
        
        if not resultado["sucesso"]:
            print(f"❌ FALHA: {resultado}")
            return False
        
        print(f"✅ PASSOU: {resultado['registros_atualizados']} registro atualizado")
        
        # Verifica se foi atualizado no CSV
        df = pd.read_csv(csv_path, sep=";", encoding="utf-8")
        row = df[df["id_registro"] == id_registros[0]].iloc[0]
        
        if row["status_gal"] == "enviado" and row["usuario_envio"] == "admin":
            print(f"✅ PASSOU: Status atualizado para 'enviado' por 'admin'")
            print(f"   Data/hora envio: {row['data_hora_envio']}")
            print(f"   Sucesso: {row['sucesso_envio']}")
        else:
            print(f"❌ FALHA: Status não foi atualizado corretamente")
            print(f"   Status: {row['status_gal']}")
            print(f"   Usuário: {row['usuario_envio']}")
            return False
        
        # Simula envio com falha do segundo
        resultado = atualizar_status_gal(
            csv_path=csv_path,
            id_registros=[id_registros[1]],
            sucesso=False,
            usuario_envio="admin",
            detalhes="Erro na conexão com GAL"
        )
        
        print(f"✅ PASSOU: {resultado['registros_atualizados']} registro atualizado (falha)")
        
        # Verifica falha
        df = pd.read_csv(csv_path, sep=";", encoding="utf-8")
        row = df[df["id_registro"] == id_registros[1]].iloc[0]
        
        if row["status_gal"] == "falha no envio" and row["sucesso_envio"] == False:
            print(f"✅ PASSOU: Status atualizado para 'falha no envio'")
            print(f"   Detalhes: {row['detalhes_envio']}")
        else:
            print(f"❌ FALHA: Falha não foi registrada corretamente")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("🧪 TESTES - Histórico com UUID e Rastreamento GAL")
    print("=" * 60)
    
    # Limpa arquivo anterior
    test_csv = "logs/test_historico.csv"
    if Path(test_csv).exists():
        Path(test_csv).unlink()
    
    test1 = test_uuid_generation()
    test2 = test_status_update()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    print(f"Test 1 (UUID Generation): {'✅ PASSOU' if test1 else '❌ FALHOU'}")
    print(f"Test 2 (Status Update):   {'✅ PASSOU' if test2 else '❌ FALHOU'}")
    
    if test1 and test2:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        
        # Mostra conteúdo final
        print("\n📄 Conteúdo final do CSV:")
        df = pd.read_csv(test_csv, sep=";", encoding="utf-8")
        print(df[["id_registro", "amostra", "codigo", "status_gal", 
                  "usuario_envio", "sucesso_envio", "detalhes_envio"]].to_string())
    else:
        print("\n❌ ALGUNS TESTES FALHARAM")
        sys.exit(1)


if __name__ == "__main__":
    main()
