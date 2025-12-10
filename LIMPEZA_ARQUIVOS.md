# 🧹 Relatório de Limpeza de Arquivos - IntegRAGal

**Data da Análise**: 10 de dezembro de 2025  
**Tamanho Total do Projeto**: 5.67 MB (excluindo .git)  
**Arquivos Identificados para Exclusão**: ~290 arquivos (~5.2 MB)

---

## 📋 RESUMO EXECUTIVO

Este relatório identifica arquivos desnecessários que podem ser excluídos do projeto IntegRAGal, organizados por categoria e prioridade. A exclusão destes arquivos não afetará o funcionamento do sistema em produção.

### Benefícios da Limpeza:
- ✅ Redução de ~91% do tamanho do repositório
- ✅ Melhor organização e navegabilidade
- ✅ Redução de tempo de backup e sincronização
- ✅ Facilita manutenção e onboarding de novos desenvolvedores

---

## 🔴 PRIORIDADE ALTA - Exclusão Imediata Recomendada

### 1. Scripts Temporários e Patches (Raiz)
```
_tmp_patch.py
tmp_fix.py
tmp_plate_preview.py
tmp_df_norm_excerpt.csv
add_dtype_fix.py
fix_encoding_safe.py
```
**Motivo**: Arquivos de correção pontual já aplicados.

---

### 2. Scripts de Análise Pontual (Raiz)
```
analise_arquivos_imagem.py
analise_cq_especifica.py
analise_ct_parenteses.py
analise_linhas.py
analise_planilha_biomanguinhos.py
analise_profunda_xls.py
analise_subdiretorio_teste.py
analise_xls_detalhada.py
busca_cq_exaustiva.py
analise_teste_subdir_resumo.txt
```
**Motivo**: Scripts de análise exploratória já executados, não fazem parte do sistema em produção.

---

### 3. Scripts de Debug (Raiz)
```
debug_cfx_detalhes.py
debug_cfx_target.py
debug_extractors.py
debug_registry.py
debug_registry2.py
debug_slug.py
df_debug.py
df_report_full.py
```
**Motivo**: Scripts de debug já utilizados, informações capturadas.

---

### 4. Scripts de Verificação (Raiz)
```
check_unicode.py
check_utf8_simple.py
verificacao_encoding_final.py
verificacao_final_codificacao.py
verifica_arquivo_principal.py
auditoria_codificacao.py
```
**Motivo**: Verificações já realizadas, sistema codificado em UTF-8.

---

### 5. Testes na Raiz (Devem estar em /tests)
```
# Padrão test_*.py (26 arquivos - ~171 KB)
test_corrections.py
test_dashboard_completo.py
test_dataframe_reporter.py
test_detector_interactive.py
test_equipment_registry.py
test_etapa2.py
test_etapa2_save.py
test_etapa3_ui.py
test_etapa4_form.py
test_etapa4_integration.py
test_etapa5_end_to_end.py
test_fase7_1_engine.py
test_fase7_e2e_consolidado.py
test_fase7_engine_integration.py
test_fase7_gal_export.py
test_fase7_historico.py
test_fase7_mapa_gui.py
test_historico_features.py
test_history_update.py
test_integration_simple.py
test_integration_temp.py
test_julho_planilhas.py
test_normalize_result.py
test_parser_temp.py
test_rules_temp.py
test_slug_logic.py

# Padrão teste_*.py (7 arquivos)
teste_cfx_export.py
teste_extractors.py
teste_fase1_4_integracao.py
teste_fase1_5_extrator.py
teste_integracao_ct.py
teste_layout_placa.py
teste_normalizacao_ct.py

# Outros testes
mapavazio_teste.py
mapa_vazio_teste_simplex.py
validate_registry_interface.py
```
**Motivo**: Testes duplicados ou temporários. Os testes oficiais estão em `/tests`.

---

### 6. Imagens Temporárias (Raiz)
```
Gemini_Generated_Image_37akv437akv437ak.png
Gemini_Generated_Image_evk2sievk2sievk2.png
Gemini_Generated_Image_f546cyf546cyf546.png
Gemini_Generated_Image_v3g2pdv3g2pdv3g2.png
```
**Motivo**: Imagens geradas por IA para testes, não utilizadas no sistema.

---

### 7. Cache e Build
```
.coverage
.ruff_cache/
```
**Motivo**: Arquivos de cache gerados automaticamente, podem ser recriados.

---

## 🟡 PRIORIDADE MÉDIA - Exclusão após Revisão

### 8. Documentação de Fases Antigas (Raiz - ~40 arquivos)
```
ETAPA1_PREPARACAO.md
ETAPA2_COMPLETO.md
ETAPA4_COMPLETO.md
ETAPA4_PLANEJAMENTO.md
ETAPA5_COMPLETO.md
FASE1_3_EXTRACTORS_CONCLUIDA.md
FASE4_DASHBOARD.md
FASE5_ANALISE_FINAL.md
FASE5_CONCLUSAO_FINAL.md
FASE6_CONCLUSAO_COMPLETA.md
FASE6_MIGRATION_LOG.txt
FASE6_RESUMO_VISUAL.txt
FASE6_VALIDATION_REPORT.txt
FASE7_CONCLUSAO_COMPLETA.md
FASE7_RESUMO_TESTES_E2E.md
PLANO_FASE5_ETAPAS.md
PLANO_FASE5_RESUMO.md
PLANO_FASE6_MIGRACAO.md
PLANO_FASE7_TESTES_E2E.md
PLANO_IMPLANTACAO_5_FASES.md
PLANO_IMPLANTACAO_FASE1.md
```
**Ação Recomendada**: Mover para `/docs/historico` ou excluir se informações já consolidadas.

---

### 9. Scripts de Migração Executados (Raiz)
```
FASE6_migrate_exams_to_json.py
FASE6_validate_registry.py
```
**Motivo**: Migrações já executadas. Considerar mover para `/scripts/legacy`.

---

### 10. Relatórios de Análise (Raiz - ~30 arquivos)
```
ANALISE_CONSOLIDADA_FASES1-5.md
ANALISE_ESTADO_ATUAL_VS_FLUXO_REVISADO.md
ANALISE_MECANISMO_INCLUSAO_EXAMES.md
ANALISE_USO_CONCOMITANTE_REDE_LOCAL.md
AUDITORIA_CODIFICACAO.txt
AUDITORIA_CODIFICACAO_FINAL.md
AUDITORIA_RESUMO_VISUAL.txt
CERTIFICADO_UTF8_FINAL.md
COMPARACAO_ANTES_DEPOIS.md
CONCLUSAO_VISUAL.txt
CORRECOES_EQUIPMENT_DETECTOR.md
RELATORIO_FASE4_INTEGRACAO.md
RELATORIO_FASE5_ANALISE.md
RELATORIO_FASES1-3_ANALISE.md
RESUMO_ALTERACOES_CT.md
RESUMO_FASE5.md
RESUMO_SOLUCAO_CONCORRENCIA.md
STATUS_CODIFICACAO_COMPLETO.md
STATUS_PROGRESSO_ATUAL.md
STATUS_PROJETO_FINAL.md
SUMARIO_FINAL_FASE4.md
relatorio_analise.txt
RESULTADO_IMPLEMENTACAO.txt
```
**Ação Recomendada**: Mover para `/docs/relatorios_desenvolvimento` ou excluir.

---

### 11. Mapas e Arquiteturas Redundantes (Raiz)
```
ARQUITETURA_CONCORRENCIA_VISUAL.md
MAPA_VISUAL_FASE4.md
MAPA_VISUAL_FASE5.md
MATRIZ_VERIFICACAO_FASE4.md
```
**Ação Recomendada**: Consolidar informações em `/docs/ARQUITETURA_TECNICA.md` e excluir.

---

### 12. Logs Temporários (~1 MB)
```
logs/dataframe_reports/          (19 arquivos de 08/12)
logs/tmp_hist.csv
logs/test_historico.csv
logs/relatorio_envio_20251204_0927.txt
logs/relatorio_envio_20251204_0941.txt
logs/relatorio_envio_20251204_0943.txt
logs/relatorio_envio_20251204_0950.txt
logs/relatorio_envio_20251204_0954.txt
logs/relatorio_envio_20251204_1000.txt
logs/resultados_por_amostra.txt
```
**⚠️ MANTER**: `logs/sistema.log` e `logs/historico_analises.csv`

---

### 13. Reports de Teste GAL (~1.6 MB, 120+ arquivos)
```
reports/gal_2025120*.csv          (90+ arquivos de teste)
reports/placa_2025120*.xlsx       (22 planilhas de teste)
reports/placa_2025120*.png        (2 imagens)
reports/historico_analises_*.csv  (backups antigos)
```
**Ação Recomendada**: 
- Manter apenas últimos 7 dias
- Mover arquivos antigos para backup externo
- Excluir arquivos de teste (prefixo `gal_` antes de 03/12)

---

### 14. Documentação em /docs (Revisar)
```
docs/ETAPA_2.1_CONCLUIDA.md
docs/ETAPA_2.2_CONCLUIDA.md
docs/ETAPA_2.3_CONCLUIDA.md
docs/ETAPA_2.5_CONCLUIDA.md
docs/ETAPA_3.1_CONCLUIDA.md
docs/ETAPA_3.2_CONCLUIDA.md
docs/ETAPA_3.3_CONCLUIDA.md
docs/ETAPA_3.4_CONCLUIDA.md
docs/ETAPA_3.5_CONCLUIDA.md
docs/ETAPA_3.6_CONCLUIDA.md
docs/FASE1_4_INTEGRACAO_CONCLUIDA.md
docs/FASE1_5_EXTRATOR_CONCLUIDA.md
docs/FASE2_CONCLUIDA.md
docs/FASE2_GUIA_COMPLETO_PROMPTS.md
docs/FASE2_IMPLEMENTACAO_DETALHADA.md
docs/FASE3_CONCLUIDA.md
docs/FASE3_PLANEJAMENTO.md
docs/FASE4_PLANEJAMENTO.md
docs/PROGRESSO_FASE2.md
docs/PROGRESSO_FASE3.md
docs/PROGRESSO_FASE4.md
docs/RESULTADOS_ETAPA_4.4.md
docs/RESULTADOS_TESTES_INTEGRACAO.md
```
**Ação Recomendada**: Mover para `/docs/legacy/historico_fases` para preservar histórico.

---

## 🟢 PRIORIDADE BAIXA - Revisar e Decidir

### 15. Configurações e Backups
```
config_backup_20251204_123549.json
config_backup_20251206_182008.json
CORRECAO_CODIFICACAO.log
```
**Ação Recomendada**: Mover para `/data/state/backups`.

---

### 16. Planilhas de Teste (Raiz)
```
exemploseegene.xlsx
placa_teste.xlsx
planilha todo.xlsx
```
**Ação Recomendada**: Mover para `/tests/fixtures` ou excluir.

---

### 17. Arquivos Diversos
```
variaveis.txt          (verificar se ainda é usado)
.env.txt               (deveria ser .env)
```

---

### 18. Diretório /analise
```
analise/relatorios_auditoria_dep.py
analise/relatorios_gal_qualidade.py
analise/relatorios_operacionais.py
analise/relatorios_qualidade_gerenciais.py
analise/testecustomtk.py
analise/vr1e2_biomanguinhos_7500.py
```
**Questão**: Este diretório faz parte do sistema ou são scripts de análise? Revisar.

---

### 19. Diretório /inclusao_testes
```
inclusao_testes/adicionar_teste.py
```
**Questão**: Ainda é usado? Consolidar com /tests se relevante.

---

## 📝 ARQUIVOS IMPORTANTES A MANTER

### Documentação Principal
- ✅ `README.md`
- ✅ `TODO.md`
- ✅ `00_LEIA_PRIMEIRO.md`
- ✅ `LEITURA_5MIN.md`
- ✅ `INSTRUCOES_INTEGRAGAL.md`
- ✅ `INSTRUCOES_DEPLOY.md`
- ✅ `GUIA_EXECUCAO_INTEGRAGAL.md`
- ✅ `GUIA_EXECUCAO_RAPIDA.md`
- ✅ `README_VISUALIZADOR_PLACA.md`
- ✅ Todos em `/docs` (FAQ, MANUAL_USUARIO, TROUBLESHOOTING, etc.)

### Código e Configuração Principal
- ✅ `main.py`
- ✅ `models.py`
- ✅ `config.json`
- ✅ `requirements.txt`
- ✅ `.gitignore`
- ✅ Todos os módulos em `/core`, `/interface`, `/extracao`, etc.

### Testes Oficiais
- ✅ Diretório `/tests` completo
- ✅ `tests/conftest.py`
- ✅ `tests/fixtures/`

### Dados de Produção
- ✅ `logs/sistema.log`
- ✅ `logs/historico_analises.csv`
- ✅ `/data/state/current_session.json`
- ✅ `/data/state/window_state.json`

---

## 🚀 SCRIPTS DE LIMPEZA AUTOMATIZADA

### Script 1: Limpeza Segura (Alta Prioridade)
Cria um script PowerShell para excluir apenas arquivos temporários e de debug com segurança.

### Script 2: Organização de Documentação
Move documentos de fases para estrutura organizada em `/docs/legacy`.

### Script 3: Limpeza de Logs e Reports Antigos
Remove logs e reports com mais de 7 dias.

---

## ⚠️ AVISOS IMPORTANTES

1. **BACKUP**: Faça backup completo antes de qualquer exclusão
2. **GIT**: Commit suas alterações atuais antes da limpeza
3. **REVISÃO**: Revise arquivos de prioridade média antes de excluir
4. **TESTES**: Execute testes após limpeza para garantir funcionamento

---

## 📊 ESTATÍSTICAS FINAIS

| Métrica | Valor |
|---------|-------|
| Tamanho Atual | 5.67 MB |
| Arquivos a Excluir | ~290 arquivos |
| Espaço a Recuperar | ~5.2 MB |
| Redução Estimada | ~91% |
| Tempo de Limpeza | ~15 minutos |

---

## 🎯 PRÓXIMOS PASSOS RECOMENDADOS

1. ✅ Criar backup completo do projeto
2. ✅ Revisar este relatório e confirmar exclusões
3. ✅ Executar scripts de limpeza por prioridade
4. ✅ Executar testes de integração
5. ✅ Commit das alterações no Git
6. ✅ Atualizar `.gitignore` para evitar acúmulo futuro

---

**Relatório gerado automaticamente em**: 10/12/2025
