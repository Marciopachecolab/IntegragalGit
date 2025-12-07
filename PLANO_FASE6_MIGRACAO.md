# üöÄ FASE 6 ‚Äî MIGRA√á√ÉO DE DADOS E VALIDA√á√ÉO

**Objetivo:** Migrar exames de CSV para JSON + validar sistema completo  
**Tempo Estimado:** 3-4 horas  
**Prioridade:** üî¥ ALTA  
**Data In√≠cio:** 7 Dezembro 2025  

---

## üìã Vis√£o Geral

```
FASE 5 (Completo)              FASE 6 (Atual)
‚îî‚îÄ UI Funcional                 ‚îú‚îÄ Migrar dados CSV ‚Üí JSON
   ‚îî‚îÄ Dialog CRUD               ‚îú‚îÄ Validar Registry
                                ‚îú‚îÄ Testar Engine completo
                                ‚îî‚îÄ Sistema Pronto para Produ√ß√£o
```

---

## üéØ Objetivos

### ‚úÖ Objetivo 1: Analisar Exames Existentes
- Listar todos exames em `banco/exames_config.csv`
- Mapear campos com ExamConfig (15 campos)
- Identificar dados faltantes/incompletos
- **Status:** Em andamento

### ‚úÖ Objetivo 2: Criar JSONs Base
- Gerar `config/exames/{slug}.json` para cada exame
- Popular com dados de CSV + metadados
- Validar schema
- **Status:** N√£o iniciado

### ‚úÖ Objetivo 3: Validar Registry Completo
- `registry.load()` com todos dados
- Verificar merge CSV+JSON
- Testar load_exam() para cada um
- **Status:** N√£o iniciado

### ‚úÖ Objetivo 4: Testes Integrados
- Engine com exames registry
- Hist√≥rico com todos alvos
- Mapa GUI refletindo exame
- Exporta√ß√£o GAL funcional
- **Status:** N√£o iniciado

---

## üìä ESTRUTURA DE TRABALHO

### ETAPA 1: An√°lise (30 min)
```
1. Ler banco/exames_config.csv
2. Ler banco/exames_metadata.csv
3. Ler config/exames/vr1e2_biomanguinhos_7500.json (template)
4. Listar campos mape√°veis
5. Identificar dados faltantes
6. Gerar script de migra√ß√£o
```

### ETAPA 2: Migra√ß√£o (1.5 h)
```
1. Criar script migrate_exams_to_json.py
2. Para cada exame:
   - Load CSV row
   - Load metadata row
   - Load template JSON
   - Merge dados
   - Validate schema
   - Save config/exames/{slug}.json
3. Verificar todos criados
4. Documentar log
```

### ETAPA 3: Valida√ß√£o (1 h)
```
1. registry.load() com todos JSONs
2. Verificar exames carregados
3. Test load_exam(slug) para cada
4. Verificar merge CSV+JSON
5. Testar UI listbox com todos
6. Gerar relat√≥rio
```

### ETAPA 4: Testes End-to-End (1 h)
```
1. Engine com exame registry
2. Hist√≥rico com campos registry
3. Mapa GUI com alvos registry
4. Exporta√ß√£o GAL com painel registry
5. Validar sa√≠da
6. Documentar resultados
```

---

## üìÇ Arquivos Envolvidos

### Leitura (Dados Fonte)
```
banco/exames_config.csv              # Lista de exames + campos base
banco/exames_metadata.csv            # Metadados + alvos/faixas
config/exames/
  ‚îî‚îÄ vr1e2_biomanguinhos_7500.json  # Template JSON
```

### Escrita (Dados Destino)
```
config/exames/
  ‚îú‚îÄ vr1_biomanguinhos_7500.json        # NEW
  ‚îú‚îÄ vr2_biomanguinhos_7500.json        # NEW
  ‚îú‚îÄ zdc_biomanguinhos_7500.json        # NEW
  ‚îú‚îÄ igm_igv.json                       # NEW
  ‚îú‚îÄ hiv_ag_ab.json                     # NEW
  ‚îî‚îÄ ... demais exames ...              # NEW
```

### Scripts
```
FASE6_migrate_exams_to_json.py        # Script migra√ß√£o
FASE6_validate_registry.py            # Script valida√ß√£o
FASE6_test_engine_integration.py      # Script testes
```

---

## üîß Migra√ß√£o Passo a Passo

### Algoritmo Principal

```python
# Pseudoc√≥digo
for exame_row in exames_config.csv:
    nome = exame_row['exame']
    
    # Load dados
    csv_data = load_csv(nome)
    metadata = load_metadata(nome)
    template = load_template('vr1e2_biomanguinhos_7500.json')
    
    # Merge
    config = merge(template, csv_data, metadata)
    
    # Validate
    if not validate_schema(config):
        log_error(f"Invalid schema for {nome}")
        continue
    
    # Save
    slug = generate_slug(nome)
    save_json(f'config/exames/{slug}.json', config)
    log_success(f"Migrated {nome} ‚Üí {slug}")

# Report
print(f"Total: {total}, Success: {success}, Failed: {failed}")
```

### Mapeamento de Campos

```
CSV ‚Üí ExamConfig JSON

exame_config.csv:
  exame              ‚Üí nome_exame
  equipamento        ‚Üí equipamento
  tipo_placa         ‚Üí tipo_placa_analitica
  kit_codigo         ‚Üí kit_codigo
  [m√≥dulo/...]       ‚Üí [derivado]

exames_metadata.csv:
  alvos              ‚Üí alvos (JSON)
  faixas_ct          ‚Üí faixas_ct (JSON)
  rp_min/rp_max      ‚Üí rps (JSON)
  controles          ‚Üí controles (JSON)

Template JSON:
  All 15 fields      ‚Üí Default/merged values
```

---

## üìà Timeline

```
09:00 ‚Äî 09:30   ETAPA 1: An√°lise (30 min)
                ‚úì Ler CSVs
                ‚úì Identificar mapeamento
                ‚úì Documentar schema

09:30 ‚Äî 11:00   ETAPA 2: Migra√ß√£o (1.5h)
                ‚úì Script migra√ß√£o
                ‚úì Criar JSONs
                ‚úì Log resultados

11:00 ‚Äî 12:00   ETAPA 3: Valida√ß√£o (1h)
                ‚úì registry.load()
                ‚úì Teste load_exam()
                ‚úì Verificar UI

12:00 ‚Äî 13:00   ETAPA 4: Testes E2E (1h)
                ‚úì Engine integration
                ‚úì Hist√≥rico
                ‚úì Mapa GUI
                ‚úì Exporta√ß√£o GAL

            TOTAL: 4 horas
```

---

## ‚úÖ Checklist

### ETAPA 1: An√°lise
- [ ] Ler exames_config.csv (quantos exames?)
- [ ] Ler exames_metadata.csv (metadata?)
- [ ] Ler template JSON (15 campos?)
- [ ] Mapear campos CSV ‚Üí JSON
- [ ] Documentar discrep√¢ncias

### ETAPA 2: Migra√ß√£o
- [ ] Script FASE6_migrate_exams_to_json.py criado
- [ ] Para cada exame:
  - [ ] Load CSV + metadata
  - [ ] Merge com template
  - [ ] Validate schema
  - [ ] Save JSON
- [ ] Log de migra√ß√£o
- [ ] Verificar todos criados

### ETAPA 3: Valida√ß√£o
- [ ] registry.load() sem erros
- [ ] Todos exames carregados
- [ ] load_exam(slug) funciona (x3 testes)
- [ ] Merge CSV+JSON correto
- [ ] UI listbox reflete tudo

### ETAPA 4: Testes E2E
- [ ] Engine com registry (1 teste)
- [ ] Hist√≥rico com alvos (1 teste)
- [ ] Mapa GUI com registry (1 teste)
- [ ] Exporta√ß√£o GAL com painel (1 teste)
- [ ] Documentar resultados

---

## üéÅ Deliverables

### Scripts
1. `FASE6_migrate_exams_to_json.py` (~150 linhas)
2. `FASE6_validate_registry.py` (~100 linhas)
3. `FASE6_test_engine_integration.py` (~150 linhas)

### Dados
1. `config/exames/*.json` ‚Äî M√∫ltiplos arquivos (1 por exame)
2. `FASE6_MIGRATION_LOG.txt` ‚Äî Log detalhado
3. `FASE6_VALIDATION_REPORT.md` ‚Äî Relat√≥rio

### Documenta√ß√£o
1. `FASE6_MIGRACAO.md` ‚Äî Este arquivo
2. `FASE6_MAPEAMENTO_CAMPOS.md` ‚Äî Schema mapping
3. `FASE6_RESULTADOS_FINAIS.md` ‚Äî Summary

---

## üöÄ In√≠cio Imediato

**Pr√≥ximo passo:** Executar ETAPA 1 (An√°lise)

```
1. Ler banco/exames_config.csv
2. Ler banco/exames_metadata.csv
3. Ler config/exames/vr1e2_biomanguinhos_7500.json
4. Documentar findings
5. Criar script migra√ß√£o
```

---

**Status:** üîÑ INICIADO  
**Tempo Restante:** ~4 horas  
**Pr√≥ximo:** An√°lise de dados existentes
