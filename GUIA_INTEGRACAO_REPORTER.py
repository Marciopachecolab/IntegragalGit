"""
GUIA DE INTEGRAÇÃO - Sistema de Relatórios de DataFrames

Este documento explica como integrar o sistema de relatórios no código existente
para capturar automaticamente informações sobre todos os DataFrames processados.
"""

# =============================================================================
# 1. IMPORTAÇÃO
# =============================================================================

from utils.dataframe_reporter import log_dataframe, generate_report, reset_reporter

# =============================================================================
# 2. INTEGRAÇÃO NOS PONTOS-CHAVE DO SISTEMA
# =============================================================================

# ----- EXTRAÇÃO (extracao/busca_extracao.py) -----

def processar_gabarito(caminho_arquivo):
    """Exemplo de integração na leitura do gabarito."""
    # ... código existente ...
    df_extracao = pd.read_excel(caminho_arquivo, ...)
    
    # >>> ADICIONAR: Registrar DataFrame
    log_dataframe(
        df_extracao,
        name="df_gabarito_extracao",
        stage="extracao",
        metadata={
            "arquivo": caminho_arquivo,
            "usuario": app_state.usuario_logado,
            "exame": app_state.exame_selecionado
        }
    )
    
    return df_extracao


# ----- LEITURA DE RESULTADOS (services/analysis_service.py ou similar) -----

def ler_resultados_equipamento(caminho_arquivo):
    """Exemplo de integração na leitura de resultados do equipamento."""
    # ... código existente ...
    df_resultados = pd.read_excel(caminho_arquivo, ...)
    
    # >>> ADICIONAR: Registrar DataFrame
    log_dataframe(
        df_resultados,
        name="df_resultados",
        stage="leitura_equipamento",
        metadata={
            "arquivo": caminho_arquivo,
            "equipamento": app_state.equipamento_detectado or "desconhecido",
            "timestamp": datetime.now().isoformat()
        }
    )
    
    return df_resultados


# ----- NORMALIZAÇÃO -----

def normalizar_dados(df_resultados, df_extracao):
    """Exemplo de integração na normalização."""
    # ... código existente de normalização ...
    df_norm = realizar_normalizacao(df_resultados, df_extracao)
    
    # >>> ADICIONAR: Registrar DataFrame
    log_dataframe(
        df_norm,
        name="df_norm",
        stage="normalizacao",
        metadata={
            "linhas_entrada": len(df_resultados),
            "linhas_saida": len(df_norm),
            "exame": app_state.exame_selecionado,
            "alvos": list(alvos_detectados)
        }
    )
    
    return df_norm


# ----- ANÁLISE -----

def executar_analise(df_norm):
    """Exemplo de integração na análise."""
    # ... código existente de análise ...
    df_final = aplicar_regras_analise(df_norm)
    
    # >>> ADICIONAR: Registrar DataFrame
    log_dataframe(
        df_final,
        name="df_final",
        stage="analise",
        metadata={
            "exame": app_state.exame_selecionado,
            "usuario": app_state.usuario_logado,
            "lote": app_state.lote,
            "arquivo_corrida": app_state.arquivo_corrida,
            "data_corrida": app_state.data_corrida,
            "regras_aplicadas": True
        }
    )
    
    # Salvar no app_state
    app_state.resultados_analise = df_final
    
    return df_final


# ----- PROCESSAMENTO FINAL -----

def processar_resultados(df_final):
    """Exemplo de integração no processamento final."""
    # ... código existente ...
    df_processado = aplicar_formatacao_final(df_final)
    
    # >>> ADICIONAR: Registrar DataFrame
    log_dataframe(
        df_processado,
        name="df_processado",
        stage="processamento",
        metadata={
            "transformacoes": ["formatacao", "validacao", "laudo"],
            "linhas_processadas": len(df_processado)
        }
    )
    
    return df_processado


# ----- HISTÓRICO -----

def gerar_historico(df_final, exame, usuario, lote, arquivo_corrida):
    """Exemplo de integração na geração do histórico."""
    # ... código existente ...
    df_hist = construir_dataframe_historico(df_final, ...)
    
    # >>> ADICIONAR: Registrar DataFrame ANTES de salvar
    log_dataframe(
        df_hist,
        name="df_hist",
        stage="historico",
        metadata={
            "destino": "logs/historico_analises.csv",
            "exame": exame,
            "usuario": usuario,
            "lote": lote,
            "arquivo_corrida": arquivo_corrida,
            "formato": "agrupado" if exame in EXAMES_AGRUPADOS else "individual"
        }
    )
    
    # Verificar se existe arquivo anterior
    if os.path.exists(caminho_csv):
        df_existente = pd.read_csv(caminho_csv, sep=";")
        
        # >>> ADICIONAR: Registrar DataFrame existente
        log_dataframe(
            df_existente,
            name="df_existente",
            stage="historico",
            metadata={
                "origem": "arquivo_csv",
                "caminho": caminho_csv,
                "operacao": "leitura_anterior"
            }
        )
    
    # Salvar histórico...
    df_hist.to_csv(caminho_csv, ...)
    
    return df_hist


# =============================================================================
# 3. GERAÇÃO DO RELATÓRIO FINAL
# =============================================================================

# No final do processamento completo (ex: ao clicar em "Finalizar" na GUI)

def finalizar_processamento():
    """Gera relatório final de todos os DataFrames processados."""
    try:
        # ... código existente de finalização ...
        
        # >>> ADICIONAR: Gerar relatório final
        print("\n" + "="*80)
        print("GERANDO RELATÓRIO DE DATAFRAMES...")
        print("="*80)
        
        report_text = generate_report()
        print(report_text)
        
        # Opcional: Mostrar mensagem na GUI
        messagebox.showinfo(
            "Relatório Gerado",
            "Relatório de DataFrames salvo em:\n"
            "logs/dataframe_reports/\n\n"
            "Verifique os arquivos CSV para amostras dos dados."
        )
        
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")


# =============================================================================
# 4. RESET NO INÍCIO DE NOVA SESSÃO
# =============================================================================

# No início de uma nova análise (ex: ao abrir a janela de análise)

def iniciar_nova_analise():
    """Inicia nova sessão de análise."""
    # >>> ADICIONAR: Resetar reporter para nova sessão
    reset_reporter()
    
    # ... resto do código de inicialização ...


# =============================================================================
# 5. EXEMPLO DE INTEGRAÇÃO EM FLUXO COMPLETO
# =============================================================================

def fluxo_completo_analise():
    """Exemplo de fluxo completo com relatórios integrados."""
    
    # Resetar reporter
    reset_reporter()
    
    # 1. Extração
    df_extracao = processar_gabarito(arquivo_gabarito)
    log_dataframe(df_extracao, "df_gabarito_extracao", "extracao", 
                 metadata={"arquivo": arquivo_gabarito})
    
    # 2. Leitura de resultados
    df_resultados = ler_resultados_equipamento(arquivo_resultados)
    log_dataframe(df_resultados, "df_resultados", "leitura_equipamento",
                 metadata={"arquivo": arquivo_resultados})
    
    # 3. Normalização
    df_norm = normalizar_dados(df_resultados, df_extracao)
    log_dataframe(df_norm, "df_norm", "normalizacao")
    
    # 4. Análise
    df_final = executar_analise(df_norm)
    log_dataframe(df_final, "df_final", "analise")
    
    # 5. Processamento
    df_processado = processar_resultados(df_final)
    log_dataframe(df_processado, "df_processado", "processamento")
    
    # 6. Histórico
    df_hist = gerar_historico(df_final, exame, usuario, lote, arquivo_corrida)
    log_dataframe(df_hist, "df_hist", "historico")
    
    # 7. Gerar relatório final
    report_text = generate_report()
    print(report_text)
    
    return df_final


# =============================================================================
# 6. LOCALIZAÇÃO DOS ARQUIVOS GERADOS
# =============================================================================

"""
Estrutura de diretórios criada:

logs/
└── dataframe_reports/
    ├── YYYYMMDD_HHMMSS_df_gabarito_extracao_extracao_sample.csv
    ├── YYYYMMDD_HHMMSS_df_resultados_leitura_equipamento_sample.csv
    ├── YYYYMMDD_HHMMSS_df_norm_normalizacao_sample.csv
    ├── YYYYMMDD_HHMMSS_df_final_analise_sample.csv
    ├── YYYYMMDD_HHMMSS_df_processado_processamento_sample.csv
    ├── YYYYMMDD_HHMMSS_df_hist_historico_sample.csv
    ├── YYYYMMDD_HHMMSS_summary.txt          # Relatório resumido
    └── YYYYMMDD_HHMMSS_reports.json         # Relatório completo JSON
    
Onde YYYYMMDD_HHMMSS é o timestamp da sessão (ex: 20251208_143025)
"""


# =============================================================================
# 7. PRINCIPAIS PONTOS DE INTEGRAÇÃO NO CÓDIGO EXISTENTE
# =============================================================================

"""
ARQUIVOS A MODIFICAR:

1. extracao/busca_extracao.py
   - Adicionar log_dataframe após leitura do gabarito
   - Linha ~200-300 (onde df_extracao é criado)

2. services/analysis_service.py ou analise/relatorios_*.py
   - Adicionar log_dataframe após leitura de resultados
   - Adicionar log_dataframe após normalização
   - Adicionar log_dataframe após análise final
   - Linhas onde df_resultados, df_norm, df_final são criados

3. relatorios/gerar_relatorios.py
   - Adicionar log_dataframe antes de salvar histórico
   - Adicionar log_dataframe ao ler histórico existente
   - Linhas ~50-150 (função gerar_historico_csv)

4. utils/gui_utils.py (TabelaComSelecaoSimulada)
   - Adicionar generate_report() ao finalizar processamento
   - Linha ~600-700 (método de finalização)

5. main.py ou interface principal
   - Adicionar reset_reporter() ao iniciar nova análise
   - Adicionar generate_report() ao fechar sessão
"""
