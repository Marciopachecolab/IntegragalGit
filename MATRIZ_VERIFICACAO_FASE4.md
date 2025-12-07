# MATRIZ DE VERIFICA√á√ÉO - FASE 4
## Checklist T√©cnico Detalhado

---

## 1. ENGINE (universal_engine.py)

### 1.1 Faixas CT do Registry
- [ ] **Motor l√™ cfg.faixas_ct ao inv√©s de config_regras**
  - Localiza√ß√£o: `_aplicar_regras_ct_e_interpretacao()` linha 263
  - Verificar: `ct_detect_max = cfg.faixas_ct["detect_max"]`
  - Fallback: Se cfg vazio, usar config_regras (compatibilidade)
  - **Status:** ‚ùå N√£o implementado (usa config_regras.get())

- [ ] **Valores padr√£o coerentes**
  - detect_max: 37-38
  - inconc_min: 37-38.01
  - inconc_max: 40-45
  - rp_min: 15
  - rp_max: 35
  - **Status:** ‚úì Registry tem defaults

### 1.2 Normaliza√ß√£o de Alvos
- [ ] **Alvos normalizados via cfg.normalize_target()**
  - Localiza√ß√£o: `_aplicar_regras_ct_e_interpretacao()` e _determine_status_corrida()
  - Verificar: Onde h√° refer√™ncia a alvo, usar normalize_target()
  - Exemplo: `alvo_norm = cfg.normalize_target(alvo)`
  - **Status:** ‚ùå N√£o implementado

- [ ] **Resultado coluna consolidado**
  - Verificar: Se alvo="INFA" e alvo="INF A" v√™m em colunas diferentes, consolidar
  - **Status:** ‚ùå Sem consolida√ß√£o

### 1.3 Blocos e Agrupamento
- [ ] **Blocos calculados via cfg.bloco_size()**
  - Localiza√ß√£o: `_determine_status_corrida()` e agrupamentos
  - Verificar: `bloco = cfg.bloco_size()`
  - Exemplo: Se esquema_agrupamento="96->48", retorna 2
  - **Status:** ‚ùå N√£o implementado

- [ ] **Po√ßos agrupados conforme bloco_size()**
  - Verificar: Se 96 po√ßos dividir por 2 (bloco_size), gera 48 grupos
  - **Status:** ‚ùå N√£o agrupado

### Pontua√ß√£o: 0/8 ‚ùå

---

## 2. HIST√ìRICO (history_report.py)

### 2.1 Registry Uso B√°sico
- [x] **cfg = get_exam_cfg(exame) chamado**
  - Localiza√ß√£o: Linha 7
  - **Status:** ‚úì Implementado

- [ ] **cfg.alvos iterado para gerar colunas**
  - Localiza√ß√£o: Linha ~123
  - Verificar: `for alvo in cfg.alvos:` ao inv√©s de _find_ct_col()
  - **Status:** ‚úì Parcial (alvos buscados mas n√£o completamente)

### 2.2 Normaliza√ß√£o de Alvos
- [ ] **cfg.normalize_target() aplicado**
  - Localiza√ß√£o: Linha ~133
  - Verificar: `alvo_norm = cfg.normalize_target(alvo)`
  - Uso: Nomes de colunas "ALV0_NORM - R" / "ALVO_NORM - CT"
  - **Status:** ‚ùå N√£o implementado

- [ ] **mapa_alvos aplicado**
  - Verificar: Se cfg.mapa_alvos = {"INFA": "INF A"}, resultado usa "INF A"
  - **Status:** ‚ùå N√£o aplicado

### 2.3 C√≥digo de Resultado
- [x] **_map_result() mapeia para 1/2/3**
  - Verificar: 1=Detectado, 2=ND, 3=Inconclusive
  - **Status:** ‚úì Implementado (linhas 13-46)

- [x] **_fmt_ct() formata com 3 casas decimais**
  - Verificar: "x,xxx" (v√≠rgula como separador)
  - **Status:** ‚úì Implementado (linhas 50-65)

### 2.4 Status GAL
- [x] **CN/CP marcados como "tipo nao enviavel"**
  - Localiza√ß√£o: Linhas 169-175
  - **Status:** ‚úì Implementado

- [x] **C√≥digo n√£o num√©rico marcado como "tipo nao enviavel"**
  - **Status:** ‚úì Implementado

### Pontua√ß√£o: 4/8 (50%) üü°

---

## 3. MAPA (plate_viewer.py)

### 3.1 Carregamento exam_cfg
- [ ] **exam_cfg carregado em from_df()**
  - Localiza√ß√£o: `from_df()` classmethod, linha ~100
  - Verificar: `if exame: model.exam_cfg = get_exam_cfg(exame)`
  - **Status:** ‚ùå N√£o implementado

- [ ] **exam_cfg acess√≠vel em outros m√©todos**
  - Verificar: `self.exam_cfg` dispon√≠vel em `_get_well_color()`, etc.
  - **Status:** ‚ùå N√£o dispon√≠vel

### 3.2 Faixas CT para RP
- [ ] **RP colorido conforme cfg.faixas_ct**
  - Localiza√ß√£o: Onde RP √© processado (linha ~250)
  - Verificar: `if ct in [rp_min, rp_max]: cor = verde`
  - **Status:** ‚ùå RP com cor azul fixa (n√£o din√¢mica)

- [ ] **RP fora de faixa colorido diferente**
  - Verificar: Se CT > rp_max ou < rp_min, cor diferente
  - **Status:** ‚ùå N√£o diferenciado

### 3.3 Blocos Din√¢micos
- [ ] **Bloco size do registry usado**
  - Localiza√ß√£o: `from_df()`, linha ~80
  - Verificar: `if group_size is None: group_size = model.exam_cfg.bloco_size()`
  - **Status:** ‚ùå N√£o implementado

- [ ] **Po√ßos agrupados conforme bloco_size**
  - Verificar: Visualiza√ß√£o mostra grupos corretos
  - **Status:** ‚ùå N√£o agrupado

### 3.4 Controles Din√¢micos
- [ ] **Controles buscados em cfg.controles**
  - Localiza√ß√£o: Onde CN/CP s√£o detectados (linha ~220)
  - Verificar: `is_control = (code in cfg.controles["cn"] or code in cfg.controles["cp"])`
  - **Status:** ‚ùå Hardcoded CN/CP

- [ ] **Controles coloridos em azul**
  - Verificar: Cor controlada por cfg (se fornecido)
  - **Status:** ‚úì Azul sim, mas n√£o din√¢mico

### 3.5 Normaliza√ß√£o de Alvos
- [ ] **Alvos normalizados na exibi√ß√£o**
  - Verificar: Se cfg.mapa_alvos = {"SC2": "SARS-COV-2"}, exibe "SARS-COV-2"
  - **Status:** ‚ùå N√£o normalizado

### Pontua√ß√£o: 1/11 (9%) üî¥

---

## 4. EXPORTA√á√ÉO GAL (main.py + envio_gal.py)

### 4.1 Registry em main.py
- [x] **_formatar_para_gal() recebe exam_cfg**
  - Localiza√ß√£o: Par√¢metro da fun√ß√£o
  - **Status:** ‚úì Implementado (linha 1)

- [x] **cfg = get_exam_cfg(exame) se n√£o passado**
  - Localiza√ß√£o: Linhas 2-3
  - **Status:** ‚úì Implementado

### 4.2 Kit e Panel
- [x] **cfg.kit_codigo usado**
  - Localiza√ß√£o: Linha ~35
  - Verificar: `df_out["kit"] = str(cfg.kit_codigo or "427")`
  - **Status:** ‚úì Implementado

- [x] **cfg.panel_tests_id usado**
  - Localiza√ß√£o: Linha ~40
  - Verificar: `df_out["painel"] = cfg.panel_tests_id or "1"`
  - **Status:** ‚úì Implementado

### 4.3 Export Fields
- [x] **cfg.export_fields iterado**
  - Localiza√ß√£o: Linhas 47-55
  - **Status:** ‚úì Implementado

- [x] **Fallback para padr√£o se vazio**
  - **Status:** ‚úì Implementado

### 4.4 Filtro Export√°vel
- [ ] **Controles verificados com cfg.controles**
  - Localiza√ß√£o: Fun√ß√£o `_exportavel()` ou equivalente
  - Verificar: `if code in cfg.controles["cn"]: return False`
  - **Status:** ‚ùå Usa hardcoded "CN"/"CP"

- [x] **Num√©ricos apenas**
  - Verificar: `code.isdigit()`
  - **Status:** ‚úì Implementado

### 4.5 Mapeamento de Resultado
- [ ] **Mapeamento 1/2/3/"" completo**
  - Localiza√ß√£o: Fun√ß√£o `_map_result()`
  - Verificar: Cobre todos casos (detectado, ND, inconclusivo, inv√°lido)
  - **Status:** ‚ö†Ô∏è Parcial (falta mapeamento de inv√°lido -> "")

- [x] **Mapeia "ALVO - X" format**
  - **Status:** ‚úì Pode mapear se existir

### 4.6 Painel por Exame
- [ ] **Gera CSV por panel_tests_id**
  - Localiza√ß√£o: envio_gal.py (n√£o visto em main.py)
  - Verificar: Arquivo `painel_1.csv`, `painel_2.csv`, etc.
  - **Status:** ‚ùå N√£o implementado

- [ ] **Separa analitos conforme export_fields**
  - Verificar: Painel 1 tem export_fields[1], etc.
  - **Status:** ‚ùå N√£o separado

### Pontua√ß√£o: 6/10 (60%) üü°

---

## 5. SUPORTE INFRAESTRUTURA

### 5.1 ExamRegistry Opera√ß√£o
- [x] **Carregamento CSV OK**
  - Localiza√ß√£o: exam_registry.py `_load_from_csv()`
  - **Status:** ‚úì Implementado

- [x] **Carregamento JSON/YAML OK**
  - Localiza√ß√£o: exam_registry.py `_load_from_json()`
  - **Status:** ‚úì Implementado

- [x] **Merge CSV+JSON OK**
  - Localiza√ß√£o: exam_registry.py `_merge_configs()`
  - **Status:** ‚úì Implementado

- [x] **normalize_target() funciona**
  - Localiza√ß√£o: ExamConfig.normalize_target()
  - **Status:** ‚úì Implementado

- [x] **bloco_size() funciona**
  - Localiza√ß√£o: ExamConfig.bloco_size()
  - **Status:** ‚úì Implementado

### 5.2 JSON Configs
- [x] **Arquivo base existe**
  - Localiza√ß√£o: config/exams/
  - **Status:** ‚úì Arquivo JSON carreg√°vel

- [ ] **Todos exames com JSON**
  - Verificar: VR1E2, ZDC, etc. t√™m JSON
  - **Status:** ‚ö†Ô∏è Alguns podem faltar

### Pontua√ß√£o: 7/7 (100%) ‚úì

---

## 6. RESUMO GERAL

| Componente | Implementa√ß√£o | Prioridade | Score | Status |
|-----------|---|---|---|---|
| **1. Motor** | 0/8 (0%) | üî¥ P0 | 0% | üî¥ Cr√≠tico |
| **2. Hist√≥rico** | 4/8 (50%) | üü† P1 | 50% | üü° Parcial |
| **3. Mapa** | 1/11 (9%) | üî¥ P0 | 9% | üî¥ Cr√≠tico |
| **4. Exporta√ß√£o** | 6/10 (60%) | üü† P1 | 60% | üü° Parcial |
| **5. Infraestrutura** | 7/7 (100%) | ‚úì | 100% | ‚úì OK |
| **TOTAL** | 18/44 | - | **41%** | **üî¥ Incompleto** |

---

## 7. ITENS FALTANTES (Cr√≠ticos)

### üî¥ P0 - Quebra funcionalidade:
- [ ] Motor: usar cfg.faixas_ct (0/8)
- [ ] Mapa: carregar exam_cfg (1/11)

### üü† P1 - Funcionalidade degradada:
- [ ] Hist√≥rico: normalize_target() (4/8)
- [ ] Exporta√ß√£o: cfg.controles dinamicamente (6/10)

### üü° P2 - Robustez:
- [ ] Exporta√ß√£o: gerar CSV por painel (envio_gal.py)
- [ ] Testes unit√°rios

---

## 8. ESFOR√áO ESTIMADO POR ITEM

| Item | Horas | Complexidade | Teste |
|------|-------|-------|------|
| Motor faixas_ct | 0.5 | Baixa | 15 min |
| Motor normalize_target | 0.5 | Baixa | 15 min |
| Motor bloco_size | 1 | M√©dia | 30 min |
| Mapa exam_cfg | 0.5 | Baixa | 15 min |
| Mapa RP faixas | 1 | M√©dia | 30 min |
| Mapa blocos | 1 | M√©dia | 30 min |
| Mapa controles din√¢micos | 0.5 | Baixa | 15 min |
| Hist√≥rico normalize_target | 0.5 | Baixa | 15 min |
| Hist√≥rico mapa_alvos | 0.25 | Baixa | 10 min |
| Exporta√ß√£o cfg.controles | 0.5 | Baixa | 15 min |
| Exporta√ß√£o painel CSV | 1 | M√©dia | 30 min |
| **TOTAL** | **7.75h** | - | **2h 45min** |

---

## 9. SEQU√äNCIA RECOMENDADA

### Sprint 1 (P0 - 3h):
1. Motor: faixas_ct (0.5h + teste)
2. Motor: normalize_target (0.5h + teste)
3. Mapa: exam_cfg load (0.5h + teste)
4. Mapa: RP faixas (1h + teste)

### Sprint 2 (P1 - 3h):
5. Hist√≥rico: normalize_target (0.5h + teste)
6. Exporta√ß√£o: cfg.controles (0.5h + teste)
7. Mapa: blocos (1h + teste)
8. Motor: bloco_size (1h + teste)

### Sprint 3 (P2 - 1.75h):
9. Exporta√ß√£o: painel CSV (1h + teste)
10. Testes integra√ß√£o (0.75h)

---

## 10. VALIDA√á√ÉO FINAL

Ap√≥s implementa√ß√£o, verificar:
- [ ] Motor gera df_final com alvos normalizados
- [ ] Hist√≥rico CSV tem colunas "ALVO - R" e "ALVO - CT"
- [ ] Mapa mostra cores corretas para RP conforme faixa
- [ ] Blocos agrupam po√ßos conforme bloco_size()
- [ ] Exporta√ß√£o GAL filtra CN/CP dinamicamente
- [ ] Painel CSV gerado com export_fields corretos
- [ ] Testes unit√°rios passam (motor, mapa, hist√≥rico, exporta√ß√£o)
- [ ] Testes integra√ß√£o passam (fluxo completo)

---

**Gerado:** 7 de dezembro de 2025  
**√öltima atualiza√ß√£o:** Dashboard inicial
