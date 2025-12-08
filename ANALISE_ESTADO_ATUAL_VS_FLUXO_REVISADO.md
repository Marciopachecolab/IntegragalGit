# 📊 ANÁLISE: ESTADO ATUAL vs FLUXO REVISADO

**Data:** 2025-12-07  
**Objetivo:** Mapear o que já existe vs o que precisa ser implementado

---

## 🎯 RESUMO EXECUTIVO

O sistema **PARCIALMENTE implementou** a arquitetura universal. Alguns componentes estão prontos, outros precisam refatoração ou são novos.

**Status Geral:**
- ✅ **40%** da arquitetura proposta já existe
- 🟡 **40%** precisa refatoração/complementação
- ❌ **20%** não existe ou precisa ser criado do zero

---

## 📋 ESTRUTURA ATUAL DO FLUXO

```
MENU PRINCIPAL (services/menu_handler.py)
│
├─ 1. Mapeamento da Placa ✅ EXISTE
│  └─ abrir_busca_extracao() → extracao/busca_extracao.py
│     ├─ carregar_dados_extracao()
│     └─ Armazena em: app_state.dados_extracao
│
├─ 2. Realizar Análise ✅ EXISTE (mas precisa refatoração)
│  └─ realizar_analise() → services/analysis_service.py
│     ├─ AnalysisService.executar_analise()
│     └─ Chama: services/universal_engine.py
│
├─ 3. Visualizar Resultados ✅ EXISTE
│  └─ mostrar_resultados_analise()
│
├─ 4. Enviar GAL ✅ EXISTE
│  └─ enviar_para_gal() → exportacao/envio_gal.py
│
├─ Administração ✅ EXISTE (novo, mas basicamente GUI)
├─ Gerenciar Usuários ✅ EXISTE
├─ Incluir Novo Exame ✅ EXISTE
└─ Relatórios ✅ EXISTE
```

---

## 🔄 PASSO 0: CADASTRO DE NOVO EXAME

### FLUXO REVISADO ESPERADO:
```
User: GUI → "Incluir Novo Exame"
├─ Preenche: nome, alvos, CTs, regras, fórmulas
└─ Salva em: banco/regras_analise_metadata.csv + JSON
```

### ESTADO ATUAL:
```
✅ GUI EXISTE: inclusao_testes/adicionar_teste.py
   └─ AdicionarTesteApp → CadastrosDiversosWindow

✅ BANCO EXISTE: banco/exames_config.csv
   └─ Campos: exame, modulo_analise, tipo_placa, numero_kit, equipamento

❌ REGRAS NÃO SINCRONIZAM: banco/regras_analise_metadata.csv
   └─ Existe arquivo, mas GUI NÃO o atualiza ao cadastrar novo exame!
   └─ User precisa adicionar manualmente

❌ JSON NÃO É CRIADO: config/exams/{slug}.json
   └─ Existe padrão no ExamRegistry, mas não é auto-gerado

⚠️ EQUIPAMENTOS: banco/equipamentos.csv
   └─ Existe arquivo, mas estrutura XLSX não é mapeada!
   └─ Não há como User cadastrar características do XLSX

📍 CONCLUSÃO: GUI parcial, faltam variáveis críticas
```

---

## 🔄 PASSO 1: EXTRAÇÃO DE DADOS

### FLUXO REVISADO ESPERADO:
```
User: Abre arquivo → Sistema AUTO-DETECTA equipamento
├─ Lê estrutura XLSX
├─ Identifica: "É 7500? CFX96? QuantStudio?"
├─ User mapeia placa (visual, drag-drop)
└─ Sistema valida CN/CP
```

### ESTADO ATUAL:
```
✅ FUNÇÃO PRINCIPAL EXISTE: extracao/busca_extracao.py
   ├─ carregar_dados_extracao(main_window)
   └─ Retorna: (dados_extracao, parte_placa)

✅ MAPEAMENTO VISUAL EXISTE
   └─ Interface com placa 96 poços (ou 48)
   └─ User seleciona poços para CN, CP, amostras

✅ ARMAZENAMENTO NO APP_STATE
   ├─ app_state.dados_extracao = DataFrame
   ├─ app_state.parte_placa = 1 ou 2
   └─ app_state.mapeamento_placa = ? (não explícito)

❌ AUTO-DETECÇÃO NÃO EXISTE
   └─ Sistema NÃO detecta automaticamente qual equipamento é
   └─ User precisa saber qual arquivo abrir (manual)

❌ EQUIPMENTREGISTRY NÃO ESTÁ INTEGRADO
   └─ Existe em exam_registry.py, mas:
   └─ Não há função para detectar padrão XLSX
   └─ Não há mapeamento de estrutura do arquivo

❌ VALIDAÇÃO DE CN/CP NÃO EXPLÍCITA
   └─ Sistema carrega dados, mas não valida controles nesta etapa

📍 CONCLUSÃO: Mapeamento OK, detecção faltando
```

---

## 🔄 PASSO 2: ANÁLISE (MOTOR UNIVERSAL)

### FLUXO REVISADO ESPERADO:
```
User: Seleciona exame + arquivo corrida
├─ Sistema DETECTA equipamento (lendo arquivo)
├─ Motor universal carrega config (ExamRegistry)
├─ Extrai dados com extrator correto
├─ Aplica lógica: CT < Max?
├─ Valida regras: 2+ alvos?
├─ Avalia fórmulas matemáticas
├─ Valida CN/CP
└─ Salva em histórico com status "não enviado"
```

### ESTADO ATUAL:
```
✅ ANÁLISE SERVICE EXISTE: services/analysis_service.py
   ├─ AnalysisService(app_state)
   ├─ analisar_corrida(exame, arquivo_resultados, arquivo_extracao, lote)
   └─ executar_analise(app_state, parent_window, exame, lote)

✅ MOTOR UNIVERSAL EXISTE: services/universal_engine.py
   ├─ UniversalEngine classe
   ├─ processar_exame(exame, df_resultados, df_extracao, lote)
   ├─ Funções auxiliares: _ler_e_normalizar_arquivo(), etc
   └─ Integração com ExamRegistry

✅ EXAM REGISTRY EXISTE: services/exam_registry.py
   ├─ ExamConfig dataclass
   ├─ ExamRegistry classe
   ├─ Carrega de: banco/exames_config.csv + banco/regras_analise_metadata.csv
   ├─ Sobrescreve com: config/exams/{slug}.json
   └─ Métodos: load(), get(nome_exame)

❌ AUTO-DETECÇÃO DE EQUIPAMENTO NÃO EXISTE
   └─ Sistema usa ExamRegistry mas NÃO detecta qual equipamento
   └─ Não há EquipmentRegistry implementado
   └─ Não há mapeamento de padrão XLSX para equipamento

❌ DETECÇÃO DE ESTRUTURA XLSX NÃO EXISTE
   └─ Sistema não analisa: "Este arquivo é 7500 ou CFX96?"
   └─ User precisa selecionar equipamento manualmente
   └─ Sem extrator específico para cada máquina

❌ FÓRMULAS MATEMÁTICAS NÃO IMPLEMENTADAS
   └─ Existe framework (config tem campo "formulas")
   └─ Mas não há code que AVALIA expressões
   └─ Não há eval() seguro ou parser de fórmulas

❌ REGRAS EXTRA NÃO IMPLEMENTADAS
   └─ Config tem espaço para "regras_extra"
   └─ Mas lógica condicional (2+ alvos, etc) não está hardcoded
   └─ Não há engine que as interpreta

✅ HISTÓRICO JÁ CAPTURA UUID
   └─ services/history_report.py
   └─ Cria: id_registro = uuid.uuid4()
   └─ Status: status_gal = "não enviado"

⚠️ ARMAZENAMENTO DE EQUIPAMENTO DETECTADO
   └─ Histórico NÃO grava qual equipamento usou
   └─ Vê-se: exame, usuario, data, alvos
   └─ Não vê-se: qual máquina (7500, CFX96, QuantStudio)

📍 CONCLUSÃO: Motor existe, mas detecção + fórmulas + regras faltam
```

---

## 🔄 PASSO 3: ENVIO GAL

### FLUXO REVISADO ESPERADO:
```
User: Clica "Enviar para GAL"
├─ Sistema busca registros com status = "não enviado"
├─ Formata conforme GAL espera
├─ Submete para API
├─ Atualiza: status_gal = "enviado", data_hora_envio, usuario_envio
└─ Resultado: ✅ Pronto
```

### ESTADO ATUAL:
```
✅ MÓDULO GAL EXISTE: exportacao/envio_gal.py
   ├─ abrir_janela_envio_gal()
   ├─ Integração com GAL API
   ├─ Envio de dados
   └─ Atualização de status

✅ HISTÓRICO TEM CAMPOS DE RASTREAMENTO
   ├─ status_gal = "não enviado" | "enviado" | "falha no envio"
   ├─ data_hora_envio
   ├─ usuario_envio
   ├─ sucesso_envio = true/false
   └─ detalhes_envio = error message

✅ FUNÇÃO PARA ATUALIZAR STATUS
   └─ services/history_report.py
   └─ atualizar_status_gal(csv_path, id_registros, sucesso, usuario_envio, detalhes)

📍 CONCLUSÃO: Envio OK, integração com histórico OK
```

---

## 🎯 COMPARAÇÃO DETALHADA

### QUADRO GERAL

| Componente | Status | Detalhes |
|-----------|--------|----------|
| **CADASTRO** | 🟡 Parcial | GUI existe, regras não sincronizam, fórmulas não capturadas |
| **EXTRAÇÃO** | 🟢 OK | Mapeamento funciona, detecção falta |
| **DETECÇÃO EQUIPAMENTO** | ❌ Falta | Não há auto-detecção de padrão XLSX |
| **EQUIPMENT REGISTRY** | ❌ Falta | Não existe, precisa ser criado |
| **EXTRACTORES** | ❌ Falta | Não há por máquina (7500, CFX96, QuantStudio) |
| **MOTOR UNIVERSAL** | 🟢 OK | Existe e funciona para VR1e2 |
| **FÓRMULAS MATEMÁTICAS** | ❌ Falta | Não há parser/eval de expressões |
| **REGRAS EXTRA** | ❌ Falta | Não há engine para lógica condicional |
| **VALIDAÇÃO CN/CP** | 🟡 Parcial | Existe em motor, mas não em extração |
| **HISTÓRICO** | 🟢 OK | UUID, status_gal, tudo implementado |
| **ENVIO GAL** | 🟢 OK | Funciona, integração OK |

---

## 📍 O QUE JÁ EXISTE

### ✅ IMPLEMENTADO E FUNCIONAL

**1. Fluxo de Menu Principal**
```
services/menu_handler.py
├─ 1. Mapeamento da Placa ✓
├─ 2. Realizar Análise ✓
├─ 3. Visualizar Resultados ✓
└─ 4. Envio GAL ✓
```

**2. Extração de Dados**
```
extracao/busca_extracao.py
├─ carregar_dados_extracao() ✓
├─ Interface mapeamento placa ✓
├─ Armazenamento em app_state ✓
└─ Validações básicas ✓
```

**3. Motor de Análise**
```
services/universal_engine.py
├─ UniversalEngine clase ✓
├─ Leitura de arquivo ✓
├─ Normalização de dados ✓
├─ Integração com ExamRegistry ✓
└─ Aplicação de regras CT ✓
```

**4. Exam Registry**
```
services/exam_registry.py
├─ ExamRegistry classe ✓
├─ Carrega de CSVs ✓
├─ Sobrescreve com JSON ✓
├─ get(nome_exame) ✓
└─ ExamConfig dataclass ✓
```

**5. Histórico**
```
services/history_report.py
├─ UUID generation ✓
├─ Status tracking ✓
├─ Rastreamento GAL ✓
└─ atualizar_status_gal() ✓
```

**6. Envio GAL**
```
exportacao/envio_gal.py
├─ API integration ✓
├─ Formatação de dados ✓
├─ Atualização de status ✓
└─ Tratamento de erro ✓
```

**7. Cadastro de Exames**
```
inclusao_testes/adicionar_teste.py + services/cadastros_diversos.py
├─ Interface GUI ✓
├─ Salva em exames_config.csv ✓
└─ CadastrosDiversosWindow ✓
```

---

## ❌ O QUE FALTA OU PRECISA REFATORAÇÃO

### PASSO 0: CADASTRO

| Item | Status | Problema |
|------|--------|---------|
| GUI campos adicionais | ❌ Falta | Não captura: CT_RP, CT_DETECTAVEL, alvos, fórmulas, regras |
| Atualizar regras_analise_metadata.csv | ❌ Não faz | GUI salva exames_config.csv, mas ignora regras |
| Criar JSON config/exams/ | ❌ Não faz | JSON não é gerado automaticamente |
| Atualizar config.json | ❌ Não faz | active_exams, configs[exame] não são preenchidos |
| Recarregar ExamRegistry | 🟡 Parcial | Recarrega UI, mas não motor em memória |

### PASSO 1: EXTRAÇÃO

| Item | Status | Problema |
|------|--------|---------|
| Auto-detectar equipamento | ❌ Falta | Não há função que lê estrutura XLSX e identifica máquina |
| EquipmentRegistry | ❌ Falta | Não existe classe, não há registro de equipamentos |
| Mapeamento estrutura XLSX | ❌ Falta | Não há dados sobre: coluna_well, coluna_ct, linha_inicio |
| Extractores por máquina | ❌ Falta | Não há extrair_dados_7500(), extrair_dados_cfx96(), etc |

### PASSO 2: ANÁLISE

| Item | Status | Problema |
|------|--------|---------|
| Detectar equipamento | ❌ Falta | Motor não detecta qual máquina pelo arquivo |
| Parser de fórmulas | ❌ Falta | Não há código que avalia "(CT_DEN1 + CT_DEN2) / 2 < 33" |
| Regras extra (lógica) | ❌ Falta | Não há engine que interpreta "requer_dois_alvos" |
| Gravar equipamento no histórico | ❌ Falta | Histórico não salva qual máquina executou análise |
| Validação de CN/CP em análise | 🟡 Parcial | Existe código, mas não é explícito nas validações finais |

### PASSO 3: ENVIO

| Item | Status | Problema |
|------|--------|---------|
| N/A | ✅ OK | Tudo pronto |

---

## 🔗 FLUXO ATUAL (SIMPLIFICADO)

```
USER:
  1. Clica "Mapeamento da Placa"
     └─ Abre arquivo manualmente
     └─ Mapeia poços CN, CP, amostras
     └─ Salva em app_state.dados_extracao

  2. Clica "Realizar Análise"
     └─ Seleciona exame (dropdown)
     └─ Seleciona lote (texto)
     ├─ ABRE ARQUIVO novamente! (manual)
     └─ Sistema:
        ├─ Usa dados pré-extraídos de app_state
        ├─ Carrega ExamRegistry.get(exame)
        ├─ Chama UniversalEngine.processar_exame()
        ├─ Retorna resultados
        └─ Salva em histórico (UUID + status "não enviado")

  3. Clica "Visualizar Resultados"
     └─ Exibe DataFrame com dados

  4. Clica "Envio GAL"
     └─ Submete histórico para GAL API
     └─ Atualiza status para "enviado"
```

### PROBLEMAS COM FLUXO ATUAL:

```
❌ User abre arquivo 2 vezes (extração + análise)
❌ User não sabe qual equipamento usou
❌ Sistema não detecta automaticamente
❌ Sem mapeamento de estrutura XLSX por máquina
❌ Sem parser de fórmulas
❌ Sem engine de regras
❌ Histórico não rastreia qual máquina
```

---

## 🎯 O QUE PRECISA SER FEITO (PRIORIZADO)

### PRIORIDADE 1 (CRÍTICO) - Semana 1

```
1. AUTO-DETECÇÃO DE EQUIPAMENTO
   └─ Criar função: detectar_equipamento(arquivo_xlsx) → "7500" | "CFX96" | "QuantStudio"
   └─ Ler estrutura do arquivo (headers, colunas)
   └─ Retornar match score
   └─ User pode confirmar ou sobrescrever

2. EQUIPMENT REGISTRY
   └─ Criar: services/equipment_registry.py
   └─ Mapeamento: nome → config XLSX
   └─ Config: coluna_well, coluna_target, coluna_ct, linha_inicio
   └─ Validações: regras para cada máquina

3. EXTRACTORES POR MÁQUINA
   └─ Criar: services/equipments/extractores.py
   └─ extrair_7500(arquivo_xlsx, config) → DataFrame normalizado
   └─ extrair_cfx96(arquivo_xlsx, config) → DataFrame normalizado
   └─ extrair_quantstudio(arquivo_xlsx, config) → DataFrame normalizado
```

### PRIORIDADE 2 (IMPORTANTE) - Semana 2

```
4. PARSER DE FÓRMULAS
   └─ Criar: services/formula_parser.py
   └─ avaliar_formula(expressão, variáveis) → bool | float
   └─ Exemplo: "(CT_DEN1 + CT_DEN2) / 2 < 33"
   └─ Substitui variáveis e avalia
   └─ Seguro contra injeção

5. ENGINE DE REGRAS
   └─ Criar: services/rules_engine.py
   └─ aplicar_regras(regras_extra, resultados) → status
   └─ Exemplo: "requer_dois_alvos=true"
   └─ Lógica condicional customizada
```

### PRIORIDADE 3 (IMPORTANTE) - Semana 3

```
6. EXPANDIR GUI CADASTRO
   └─ Adicionar campos: CT_RP, CT_DETECTAVEL, alvos, fórmulas, regras
   └─ Ao salvar: atualizar 5 arquivos (config.csv, metadata, JSON, equipamentos, config.json)
   └─ Validação de dados

7. INTEGRAR DETECÇÃO NO FLUXO
   └─ Análise: Auto-detectar equipamento
   └─ Usar extrator correto
   └─ Gravar equipamento no histórico
```

---

## 📝 RESUMO FINAL

### ESTADO ATUAL:

```
✅ 40% implementado:
   ├─ Fluxo básico menu
   ├─ Extração de dados (mapeamento manual)
   ├─ Motor universal (analysis_service)
   ├─ ExamRegistry (carregamento de config)
   ├─ Histórico (UUID + status)
   └─ Envio GAL

🟡 40% parcial:
   ├─ Cadastro de exames (GUI existe, mas faltam campos)
   ├─ Validação CN/CP (existe código, não integrado)
   └─ Integração análise ↔ histórico

❌ 20% faltando:
   ├─ Auto-detecção de equipamento
   ├─ EquipmentRegistry
   ├─ Extractores por máquina
   ├─ Parser de fórmulas
   ├─ Engine de regras
   └─ Equipamento no histórico
```

### PRÓXIMOS PASSOS IMEDIATOS:

```
SEMANA 1: Detecção + EquipmentRegistry + Extractores
SEMANA 2: Parser de fórmulas + Rules engine
SEMANA 3: Integração completa + GUI expandida + Testes E2E
```

### RISCO ATUAL:

```
⚠️ Sistema funciona, mas de forma MANUAL:
   ├─ User abre arquivo 2 vezes
   ├─ User seleciona tudo manualmente
   ├─ Sem inteligência de detecção
   ├─ Sem rastreamento de equipamento
   └─ Sem fórmulas/regras dinâmicas

→ SOLUÇÃO: Implementar 3 prioridades acima para 100% automático
```

---

**Data:** 2025-12-07  
**Status:** ⚠️ Funcional mas incompleto  
**Próximo:** Implementar autodetecção + Equipment Registry
