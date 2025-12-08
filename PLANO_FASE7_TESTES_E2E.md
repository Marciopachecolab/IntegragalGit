# ðŸš€ FASE 7 — TESTES E2E SISTEMA COMPLETO



**Objetivo:** Validar sistema integrado com exames migrados  

**Tempo Estimado:** 2-3 horas  

**Status:** ðŸ”„ PLANEJADO  

**Data Início:** 7 Dezembro 2025  



---



## ðŸ“‹ Visão Geral



```

FASE 5 (UI)        FASE 6 (Dados)        FASE 7 (Integração) â†� ATUAL

â””â”€ Completo        â””â”€ Completo           â”œâ”€ Engine

                                         â”œâ”€ Histórico

                                         â”œâ”€ Mapa GUI

                                         â”œâ”€ Exportação

                                         â””â”€ Sistema Pronto

```



---



## ðŸŽ¯ 4 Testes Principais



### 1ï¸�âƒ£ Engine Integration Test

**Validar processamento de exame com dados registry**



```

Objetivo: Engine processa VR1e2 com alvos/faixas do registry



Fluxo:

  1. Load registry com VR1e2

  2. Load placa 48-well (VR1e2 usa 96->48)

  3. Processar com engine.analisar_placa_vr1e2_7500()

  4. Validar resultados com alvos registry: SC2, HMPV, INF A, INF B, ADV, RSV, HRV

  5. Verificar faixas_ct aplicadas (detect_max=38, inconc_min=38.01, etc)



Esperado:

  âœ“ Sem erros de processamento

  âœ“ Todos alvos calculados

  âœ“ RPs dentro de faixas_ct

  âœ“ Controles validados (CN/CP)

```



### 2ï¸�âƒ£ Histórico Test

**Validar histórico com todos alvos do registry**



```

Objetivo: Histórico gera colunas para todos alvos VR1e2



Fluxo:

  1. Executar corrida com VR1e2

  2. Gerar histórico via history_report.py

  3. Verificar colunas geradas



Esperado:

  âœ“ Colunas para SC2, HMPV, INF A, INF B, ADV, RSV, HRV

  âœ“ Colunas CT e RP para cada alvo

  âœ“ Nomenclatura normalizada (sem underscore/acentos)

  âœ“ Status_gal refletindo validação

```



### 3ï¸�âƒ£ Mapa GUI Test

**Validar plate viewer com registry**



```

Objetivo: Plate viewer abre VR1e2 com cores corretas



Fluxo:

  1. Abrir plate_viewer.py com VR1e2

  2. Verificar cores por alvo

  3. Verificar RPs exibidos

  4. Validar controles em azul



Esperado:

  âœ“ Cores diferentes por alvo

  âœ“ RPs dentro faixas_ct

  âœ“ Controles (CN/CP) identificados

  âœ“ UI responsiva, sem erros

```



### 4ï¸�âƒ£ Exportação GAL Test

**Validar exportação com panel_tests_id do registry**



```

Objetivo: GAL export funciona com panel do registry



Fluxo:

  1. Executar corrida com VR1e2

  2. Exportar para GAL via menu

  3. Validar CSV gerado



Esperado:

  âœ“ Panel_tests_id=1 aplicado

  âœ“ Export_fields mapeados corretamente

  âœ“ CN/CP não exportados

  âœ“ Arquivo GAL válido

```



---



## ðŸ“Š Estrutura de Trabalho



### ETAPA 1: Engine Integration (45 min)

```

1. Create test_fase7_engine_integration.py

2. Load registry

3. Load VR1e2 exam

4. Process 48-well plate

5. Validate outputs

6. Document results

```



### ETAPA 2: Histórico Test (30 min)

```

1. Create test_fase7_historico.py

2. Load corrida with VR1e2

3. Generate history report

4. Verify columns for all targets

5. Validate CT/RP normalization

```



### ETAPA 3: Mapa GUI Test (30 min)

```

1. Create test_fase7_mapa_gui.py

2. Load plate viewer with VR1e2

3. Verify colors per target

4. Validate RP ranges

5. Screenshot validation

```



### ETAPA 4: Exportação GAL Test (30 min)

```

1. Create test_fase7_exportacao_gal.py

2. Load corrida with VR1e2

3. Export to GAL

4. Validate CSV format

5. Verify panel_tests_id

```



### ETAPA 5: Documentação Final (30 min)

```

1. Create FASE7_TESTES_E2E.md

2. Summarize all results

3. Create SISTEMA_PRONTO_PRODUCAO.md

4. Final checklist

5. Ready for deployment

```



---



## ðŸ§ª Testes a Implementar



### test_fase7_engine_integration.py (~150 linhas)



```python

def test_vr1e2_engine_processing():

    """Test engine with VR1e2 from registry"""

    # Setup

    registry = ExamRegistry()

    registry.load()

    cfg = registry.get("vr1e2 biomanguinhos 7500")

    

    # Process plate

    results = analisar_placa_vr1e2_7500(plate_data)

    

    # Validate

    assert len(results) >= 7  # 7 targets

    for target in cfg.alvos:

        assert target in results

    assert all(15 <= rp <= 35 for rp in rps)

```



### test_fase7_historico.py (~150 linhas)



```python

def test_historico_with_vr1e2():

    """Test history report with VR1e2 from registry"""

    # Setup

    corrida_data = load_corrida_vr1e2()

    registry = ExamRegistry()

    registry.load()

    cfg = registry.get("vr1e2 biomanguinhos 7500")

    

    # Generate

    df_historico = gerar_historico(corrida_data, cfg)

    

    # Validate

    assert "SC2 - CT" in df_historico.columns

    assert "HMPV - CT" in df_historico.columns

    assert "INF A - CT" in df_historico.columns

    # ... more columns

```



### test_fase7_mapa_gui.py (~150 linhas)



```python

def test_plate_viewer_vr1e2():

    """Test plate viewer with VR1e2"""

    # Setup

    registry = ExamRegistry()

    registry.load()

    cfg = registry.get("vr1e2 biomanguinhos 7500")

    

    # Open viewer

    viewer = PlateViewerWindow(cfg=cfg, plate_data=test_data)

    

    # Validate

    assert viewer.plate_canvas is not None

    assert len(viewer.target_colors) == 7  # 7 targets

    assert viewer.status_label.cget("text") != ""

```



### test_fase7_exportacao_gal.py (~150 linhas)



```python

def test_gal_export_vr1e2():

    """Test GAL export with VR1e2"""

    # Setup

    corrida_data = load_corrida_vr1e2()

    registry = ExamRegistry()

    registry.load()

    cfg = registry.get("vr1e2 biomanguinhos 7500")

    

    # Export

    csv_bytes = exportar_gal(corrida_data, cfg)

    

    # Validate

    assert cfg.panel_tests_id in csv_content

    for field in cfg.export_fields:

        assert field in csv_content

    assert "CN" not in csv_content  # Não exporta controles

```



---



## ðŸ“ˆ Timeline



```

09:00 — 09:45   ETAPA 1: Engine Integration (45 min)

                âœ“ Test engine with registry

                âœ“ Validate processing



09:45 — 10:15   ETAPA 2: Histórico (30 min)

                âœ“ Test history generation

                âœ“ Validate columns



10:15 — 10:45   ETAPA 3: Mapa GUI (30 min)

                âœ“ Test plate viewer

                âœ“ Validate visualization



10:45 — 11:15   ETAPA 4: Exportação GAL (30 min)

                âœ“ Test GAL export

                âœ“ Validate CSV



11:15 — 11:45   ETAPA 5: Documentação (30 min)

                âœ“ Summarize results

                âœ“ Final checklist



            TOTAL: ~2.5 horas

```



---



## âœ… Checklist



- [ ] test_fase7_engine_integration.py criado e passando

- [ ] test_fase7_historico.py criado e passando

- [ ] test_fase7_mapa_gui.py criado e passando

- [ ] test_fase7_exportacao_gal.py criado e passando

- [ ] FASE7_TESTES_E2E.md documentado

- [ ] SISTEMA_PRONTO_PRODUCAO.md criado

- [ ] Todo.md Fase 7 marcado COMPLETO

- [ ] Sistema pronto para deploy



---



## ðŸŽ� Deliverables



### Testes (4 arquivos)

1. `test_fase7_engine_integration.py`

2. `test_fase7_historico.py`

3. `test_fase7_mapa_gui.py`

4. `test_fase7_exportacao_gal.py`



### Documentação (2 arquivos)

1. `FASE7_TESTES_E2E.md` — Resultados testes

2. `SISTEMA_PRONTO_PRODUCAO.md` — Status final



### Validação

- âœ… 4 testes principais passando

- âœ… Sistema integrado funcionando

- âœ… Pronto para produção



---



## ðŸš€ Início



**Próximo comando:**

```

python FASE7_create_engine_integration_test.py

```



**Tempo até conclusão:** ~2.5 horas



---



**Status:** ðŸ”„ PRONTO PARA INICIAR  

**Prioridade:** ðŸ”´ ALTA  

**Bloqueante:** Não (pode fazer em paralelo)

