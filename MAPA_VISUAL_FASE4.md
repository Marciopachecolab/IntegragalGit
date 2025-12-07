# MAPA VISUAL - FASE 4 (One-Page Reference)
## IntegraÃ§Ã£o Registry - Estado Atual e Patches NecessÃ¡rios

---

## ğŸ“Š STATUS ATUAL (41% Implementado)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�
â”‚ COMPONENTE      â”‚ IMPL. %  â”‚ CRÃ�TICO  â”‚ ESFORÃ‡O    â”‚ STATUS       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ 1. Motor        â”‚ 0%   ğŸ”´  â”‚ P0      â”‚ 2-3h      â”‚ âš ï¸� Usa CSV   â”‚
â”‚ 2. HistÃ³rico    â”‚ 50%  ğŸŸ¡  â”‚ P1      â”‚ 1h        â”‚ Parcial      â”‚
â”‚ 3. Mapa         â”‚ 9%   ğŸ”´  â”‚ P0      â”‚ 2-3h      â”‚ Sem cfg      â”‚
â”‚ 4. ExportaÃ§Ã£o   â”‚ 60%  ğŸŸ¡  â”‚ P1      â”‚ 1.5h      â”‚ BÃ¡sico OK    â”‚
â”‚ 5. Infraestruturaâ”‚ 100% âœ“  â”‚ -       â”‚ -         â”‚ Operacional  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ MÃ‰DIA GERAL     â”‚ 41%  ğŸŸ¡  â”‚          â”‚ 6-8h      â”‚ ViÃ¡vel       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## ğŸ”§ PATCHES NECESSÃ�RIOS

```
â”Œâ”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�
â”‚ # â”‚ ARQUIVO              â”‚ TEMPO   â”‚ O QUÃŠ                          â”‚
â”œâ”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ 1 â”‚ universal_engine.py  â”‚ 30 min  â”‚ Usar faixas_ct do registry     â”‚
â”‚   â”‚ (linha 263)          â”‚         â”‚ em vez de config_regras        â”‚
â”œâ”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ 2 â”‚ plate_viewer.py      â”‚ 30 min  â”‚ Carregar exam_cfg em from_df() â”‚
â”‚   â”‚ (linha 100)          â”‚         â”‚ e usar bloco_size()            â”‚
â”œâ”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ 3 â”‚ history_report.py    â”‚ 30 min  â”‚ Aplicar normalize_target()     â”‚
â”‚   â”‚ (linha 133)          â”‚         â”‚ em nomes de colunas            â”‚
â”œâ”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ 4 â”‚ main.py              â”‚ 30 min  â”‚ Usar cfg.controles em filtro   â”‚
â”‚   â”‚ (linha 115)          â”‚         â”‚ ao invÃ©s de hardcoded CN/CP    â”‚
â”œâ”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ 5 â”‚ envio_gal.py         â”‚ 60 min  â”‚ Gerar CSV por panel_tests_id   â”‚
â”‚   â”‚ (novo mÃ©todo)        â”‚         â”‚ com export_fields corretos     â”‚
â”œâ”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚   â”‚ TOTAL                â”‚ 2.5h    â”‚ ImplementaÃ§Ã£o base             â”‚
â”‚   â”‚ + Testes/ValidaÃ§Ã£o   â”‚ 1h      â”‚ Unit + IntegraÃ§Ã£o              â”‚
â”‚   â”‚ TOTAL COMPLETO       â”‚ 3.5h    â”‚                                â”‚
â””â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## ğŸ�¯ ROADMAP (Sprints)

```
SPRINT 1 (P0 - CRÃ�TICO)          SPRINT 2 (P1 - ALTO)           SPRINT 3 (P2 - MÃ‰DIO)
â”œâ”€ PATCH 1 (Motor)               â”œâ”€ PATCH 3 (HistÃ³rico)        â””â”€ PATCH 5 (Painel)
â”œâ”€ PATCH 2 (Mapa)                â”œâ”€ PATCH 4 (ExportaÃ§Ã£o)
â”‚                                â””â”€ Blocos (Motor + Mapa)
Tempo: 1h dev + 30min teste      Tempo: 1.5h dev + 30min       Tempo: 1h dev + 30min
Resultado: Core OK âœ“             Resultado: HistÃ³rico/Export   Resultado: Painel OK âœ“
                                 Resultado: Features OK âœ“      
                                 Resultado: Completo âœ“
```

---

## âš ï¸� PROBLEMAS CRÃ�TICOS (P0)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�
â”‚ PROBLEMA 1: Motor usa CSV legado, nÃ£o registry JSON         â”‚
â”‚ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”‚
â”‚ ATUAL:   ct_detect_max = config_regras.get("CT_DETECT_MAX")  â”‚
â”‚ DEVERIA: ct_detect_max = cfg.faixas_ct["detect_max"]         â”‚
â”‚ IMPACTO: Thresholds diferentes se JSON â‰  CSV                â”‚
â”‚ FIX:     PATCH 1 (30 min)                                    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�
â”‚ PROBLEMA 2: Mapa nÃ£o carrega exam_cfg, cores RP hardcoded   â”‚
â”‚ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”‚
â”‚ ATUAL:   model.exam_cfg = None  (nunca carregado)            â”‚
â”‚ DEVERIA: model.exam_cfg = get_exam_cfg(exame)                â”‚
â”‚ IMPACTO: RP colorido sempre azul (ignora faixa)              â”‚
â”‚ FIX:     PATCH 2 (30 min)                                    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## âœ… O QUE JÃ� FUNCIONA

```
âœ“ Registry carrega CSVs + JSONs + merge OK
âœ“ ExamConfig fields: alvos, faixas_ct, normalize_target(), bloco_size()
âœ“ HistÃ³rico chama get_exam_cfg() 
âœ“ _map_result() mapeia para 1/2/3
âœ“ _fmt_ct() formata com 3 casas decimais
âœ“ main.py usa normalize_target()
âœ“ kit_codigo, panel_tests_id usados
```

---

## â�Œ O QUE AINDA FALTA

```
âœ— Motor: nÃ£o usa registry faixas_ct (0%)
âœ— Mapa: nÃ£o carrega exam_cfg (9%)
âœ— NormalizaÃ§Ã£o: nÃ£o aplicada sistematicamente
âœ— Controles: hardcoded CN/CP, nÃ£o dinÃ¢micos
âœ— Blocos: nÃ£o agrupam conforme bloco_size()
âœ— Painel CSV: nÃ£o gerado por panel_tests_id
```

---

## ğŸ“ˆ ESFORÃ‡O POR ITEM (Gantt Simplificado)

```
PATCH 1 [â–ˆâ–ˆâ–ˆâ–ˆâ–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘] 30 min
PATCH 2 [â–ˆâ–ˆâ–ˆâ–ˆâ–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘] 30 min
PATCH 3 [â–ˆâ–ˆâ–ˆâ–ˆâ–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘] 30 min
PATCH 4 [â–ˆâ–ˆâ–ˆâ–ˆâ–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘] 30 min
PATCH 5 [â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘] 60 min
TESTES  [â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘] 45 min
        â”œâ”€ 0h   1h   2h   3h   4h â†’
        
TOTAL: 3.5 horas (implementaÃ§Ã£o + testes)
```

---

## ğŸ§ª TESTES RÃ�PIDOS (ValidaÃ§Ã£o)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�
â”‚ TESTE        â”‚ COMANDO / VERIFICAÃ‡ÃƒO                  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Registry OK  â”‚ cfg = get_exam_cfg("vr1e2_...")        â”‚
â”‚              â”‚ assert cfg.faixas_ct["detect_max"] > 0 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Motor OK     â”‚ df_final, meta = executar_analise()    â”‚
â”‚              â”‚ # verifica se usou registry thresholds â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Mapa OK      â”‚ model = PlateModel.from_df(df, exame)  â”‚
â”‚              â”‚ assert model.exam_cfg is not None      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ HistÃ³rico OK â”‚ gerar_historico_csv(df, exame, user)   â”‚
â”‚              â”‚ assert "INF A - R" in cols             â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Export OK    â”‚ df_gal = _formatar_para_gal(df, cfg)   â”‚
â”‚              â”‚ assert "CN" not in codigoAmostra       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## ğŸš€ DECISÃƒO RÃ�PIDA

```
â”œâ”€ SIM, implementar agora?
â”‚  â””â”€ Comece com PATCH 1 + 2 (Sprint 1, hoje?)
â”‚
â”œâ”€ SIM, mas com mais tempo?
â”‚  â””â”€ Planeje Sprint 1 para semana que vem (3 dias dev)
â”‚
â””â”€ NÃƒO, adiar?
   â””â”€ JÃ¡ estÃ¡ mapeado, aproveita quando houver janela
```

---

## ğŸ“� REFERÃŠNCIA RÃ�PIDA

| Preciso de... | Veja... | Tempo |
|---|---|---|
| Status geral | `FASE4_DASHBOARD.md` | 10 min |
| Implementar rÃ¡pido | `GUIA_IMPLEMENTACAO_RAPIDA.md` | 90 min |
| Detalhes tÃ©cnicos | `RECOMENDACOES_TECNICAS_FASE4.md` | 30 min |
| Checklist completo | `MATRIZ_VERIFICACAO_FASE4.md` | 20 min |
| AnÃ¡lise profunda | `RELATORIO_FASE4_INTEGRACAO.md` | 1h |
| Ã�ndice/NavegaÃ§Ã£o | `INDICE_DOCUMENTACAO_FASE4.md` | 5 min |

---

## ğŸ’¡ KEY INSIGHTS

```
1. REGISTRY Ã‰ SÃ“LIDO
   Base bem estruturada, jÃ¡ carrega/merge/normalize OK âœ“

2. INTEGRAÃ‡ÃƒO INCOMPLETA  
   41% implementado, componentes usam parcialmente

3. PATCHES SÃƒO PEQUENOS
   30 min cada, copy-paste code, sem redesign

4. FALLBACKS GARANTEM COMPATIBILIDADE
   Usa JSON registry se ok, senÃ£o CSV legado

5. VIÃ�VEL EM UMA SPRINT
   3-4 dias dev (1-2 pessoas), 7-8 horas total
```

---

## â�° TIMELINE ESTIMADA

```
DIA 1 (hoje)      : Revisar, Decidir
DIA 2-4           : Sprint 1 (P0, 3h dev)
DIA 5-7           : Sprint 2 (P1, 3h dev)  
DIA 8-9           : Sprint 3 (P2, 2h dev)
DIA 10-12         : Testes, ValidaÃ§Ã£o (2h)
DIA 13+           : Deploy, Monitoramento

TOTAL: ~2 semanas (com sprints consecutivos)
```

---

## ğŸ�“ CONCLUSÃƒO

**Fase 4 EstÃ¡ ViÃ¡vel.** 
- Base pronta (Registry OK)
- Patches pequenos (30-60 min cada)
- Testes simples (5-10 min cada)
- Risco baixo (fallbacks)

**PrÃ³ximo Passo: Agendar Sprint 1 (P0)**

---

**Mapa Visual:** 7 de dezembro de 2025  
**VersÃ£o:** 1.0  
**Status:** âœ… PRONTO PARA DECISÃƒO
