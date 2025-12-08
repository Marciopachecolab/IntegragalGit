# 🔍 ANÁLISE DO MECANISMO DE INCLUSÃO DE NOVOS EXAMES

**Data:** 2025-12-07  
**Status:** ⚠️ INCOMPLETO - Faltam variáveis críticas

---

## 📋 RESUMO EXECUTIVO

O mecanismo de inclusão de exames está **INCOMPLETO E NÃO SINCRONIZADO**. Existem **5 locais independentes** onde dados de exames são armazenados, mas o sistema de inclusão não atualiza todos eles simultaneamente. Isso criará **inconsistências de dados** quando um novo exame for adicionado.

**Problemas Identificados:**
1. ❌ CSV `exames_config.csv` - Atualizado via UI
2. ❌ CSV `exames_metadata.csv` - **NÃO ATUALIZADO**
3. ❌ CSV `regras_analise_metadata.csv` - **NÃO ATUALIZADO**
4. ❌ JSON `config.json` - **NÃO ATUALIZADO**
5. ❌ JSON/YAML em `config/exams/` - **OPCIONAL, não sincronizado**

---

## 🗂️ ARQUITETURA ATUAL DE ARMAZENAMENTO DE EXAMES

### 1. **banco/exames_config.csv** (PRINCIPAL)
**Arquivo:** `c:\Users\marci\downloads\integragal\banco\exames_config.csv`  
**Responsável:** Interface UI `CadastrosDiversosWindow` em `services/cadastros_diversos.py`

**Colunas Requeridas (5 campos):**
```
exame | modulo_analise | tipo_placa | numero_kit | equipamento
```

**Exemplo:**
```csv
exame,modulo_analise,tipo_placa,numero_kit,equipamento
VR1e2 Biomanguinhos 7500,analise.vr1e2_biomanguinhos_7500.analisar_placa_vr1e2_7500,48,1140,7500 Real-Time
ZDC Biomanguinhos 7500,analise.zdc_biomanguinhos_7500.analisar_placa_zdc,36,1832,7500 Real-Time
```

**Status:** ✅ Atualizado via UI quando novo exame adicionado  
**Dependência:** Nenhuma (fonte de verdade para nome e módulo)

---

### 2. **banco/exames_metadata.csv** (COMPLEMENTAR - DUPLICADO!)
**Arquivo:** `c:\Users\marci\downloads\integragal\banco\exames_metadata.csv`  
**Responsável:** NINGUÉM! Não há código que o atualiza

**Colunas (5 campos - IGUAIS a exames_config.csv):**
```
exame | modulo_analise | tipo_placa | numero_kit | equipamento
```

**Exemplo:**
```csv
"exame","modulo_analise","tipo_placa","numero_kit","equipamento"
"VR1e2 Biomanguinhos 7500","analise.vr1e2_biomanguinhos_7500.analisar_placa_vr1e2_7500","48","1140","7500 Real-Time"
```

**Problema:** ⚠️ **ARQUIVO DUPLICADO E DESINCRONIZADO**
- Não há código que o atualiza quando novo exame adicionado
- `ExamRegistry._load_from_csv()` busca dele, mas como fallback
- Pode ficar com dados antigos/incorretos

**Risco:** Se um exame estiver em `exames_config.csv` mas não em `exames_metadata.csv`, o ExamRegistry pode não carregar a metadata!

---

### 3. **banco/regras_analise_metadata.csv** (CRÍTICO - NÃO ATUALIZADO!)
**Arquivo:** `c:\Users\marci\downloads\integragal\banco\regras_analise_metadata.csv`  
**Responsável:** NINGUÉM! Não há código que o atualiza

**Colunas (11 campos):**
```
exame | CT_RP_MIN | CT_RP_MAX | CT_DETECTAVEL_MIN | CT_DETECTAVEL_MAX | 
CT_INCONCLUSIVO_MIN | CT_INCONCLUSIVO_MAX | alvos | categorias_resultado | 
status_corrida_validos | observacoes
```

**Exemplo:**
```csv
"VR1e2 Biomanguinhos 7500","15","35","10","38","38.01","40",
"SC2;HMPV;INF A;INF B;ADV;RSV;HRV",
"Detectado;Nao Detectado;Inconclusivo;Invalido",
"Valida;Invalida (CN Detectado);Invalida (CP Fora do Intervalo);Invalida (Controles Ausentes)",
"Parametros extraidos do modulo analise.vr1e2_biomanguinhos_7500 para o equipamento 7500 Real-Time"
```

**Dados Carregados por `ExamRegistry._load_from_csv()`:**

```python
# Linha 285-315 do exam_registry.py
alvos_str = regras.get("alvos", "")  # ← SC2;HMPV;INF A;... (SEMICOLON-SEPARATED)
if alvos_str:
    alvos = [a.strip() for a in str(alvos_str).split(";") if a.strip()]

faixas_ct = {
    "detect_max": _safe_float(regras.get("CT_DETECTAVEL_MAX", 38.0), 38.0),
    "inconc_min": _safe_float(regras.get("CT_INCONCLUSIVO_MIN", 38.01), 38.01),
    "inconc_max": _safe_float(regras.get("CT_INCONCLUSIVO_MAX", 40.0), 40.0),
    "rp_min": _safe_float(regras.get("CT_RP_MIN", 15.0), 15.0),
    "rp_max": _safe_float(regras.get("CT_RP_MAX", 35.0), 35.0),
}
```

**Problema:** ❌ **CRÍTICO - NÃO HÁ UI PARA ATUALIZAR ESTE ARQUIVO**
- Quando novo exame adicionado, este arquivo **NÃO é atualizado**
- Sem dados de `alvos`, o histórico não terá colunas dinâmicas!
- **Impacto direto no histórico de análises** (implementação atual depende destes alvos!)

**Variáveis Faltando:**
- [ ] `CT_RP_MIN` - Limite mínimo CT para Replicação Positiva (ex: 15)
- [ ] `CT_RP_MAX` - Limite máximo CT para Replicação Positiva (ex: 35)
- [ ] `CT_DETECTAVEL_MIN` - Limite mínimo CT para "Detectado" (ex: 10)
- [ ] `CT_DETECTAVEL_MAX` - Limite máximo CT para "Detectado" (ex: 38)
- [ ] `CT_INCONCLUSIVO_MIN` - Limite mínimo CT para "Inconclusivo" (ex: 38.01)
- [ ] `CT_INCONCLUSIVO_MAX` - Limite máximo CT para "Inconclusivo" (ex: 40)
- [ ] `alvos` - Lista de alvos separados por `;` (ex: `SC2;HMPV;INF A;INF B`)
- [ ] `categorias_resultado` - Resultados possíveis (ex: `Detectado;Não Detectado;Inconclusivo;Inválido`)
- [ ] `status_corrida_validos` - Status de corrida válidos
- [ ] `observacoes` - Notas sobre o exame

---

### 4. **configuracao/config.json** (NÃO SINCRONIZADO!)
**Arquivo:** `c:\Users\marci\downloads\integragal\configuracao\config.json`  
**Responsável:** Arquivo de configuração manual

**Seção `exams`:**
```json
{
    "exams": {
        "active_exams": [
            "VR1",
            "VR2",
            "Arbovirose",
            "Vírus Respiratórios",
            "NS1",
            "VR1e2 Biomanguinhos 7500"
        ],
        "configs": {
            "VR1e2 Biomanguinhos 7500": {
                "kit_codigo": 1140,
                "export_fields": [
                    "Sars-Cov-2",
                    "Influenzaa",
                    "Influenzab",
                    "RSV",
                    ...
                ]
            }
        }
    }
}
```

**Problema:** ⚠️ **NÃO ATUALIZADO AUTOMATICAMENTE**
- Quando novo exame adicionado via UI, este JSON **não é atualizado**
- Requer atualização manual
- `export_fields` **não estão sendo carregados** da UI

**Variáveis Faltando:**
- [ ] `active_exams` - Lista de exames ativos (não sincronizado)
- [ ] `configs[exame_name].kit_codigo` - Kit code (duplicado de exames_config.csv)
- [ ] `configs[exame_name].export_fields` - Campos para exportação GAL

---

### 5. **config/exams/ (OPCIONAL - JSON/YAML POR EXAME)**
**Diretório:** `c:\Users\marci\downloads\integragal\config\exams\`  
**Responsável:** Nenhum (manual)

**Propósito:** Sobrescrever/complementar dados do CSV via JSON/YAML  
**Exemplo esperado:** `config/exams/vr1e2_biomanguinhos_7500.json`

```json
{
    "nome_exame": "VR1e2 Biomanguinhos 7500",
    "slug": "vr1e2_biomanguinhos_7500",
    "kit_codigo": 1140,
    "tipo_placa_analitica": "48",
    "esquema_agrupamento": "96->48",
    "equipamento": "7500 Real-Time",
    "alvos": ["SC2", "HMPV", "INF A", "INF B", "ADV", "RSV", "HRV"],
    "mapa_alvos": {
        "SC2": "Sars-Cov-2",
        "HMPV": "Metapneumovírus",
        "INF A": "Influenza A",
        "INF B": "Influenza B"
    },
    "faixas_ct": {
        "detect_max": 38.0,
        "inconc_min": 38.01,
        "inconc_max": 40.0,
        "rp_min": 15.0,
        "rp_max": 35.0
    },
    "export_fields": ["Sars-Cov-2", "Influenza A", "Influenza B", "RSV", "ADV", "HRV", "Metapneumovírus"],
    "panel_tests_id": "1",
    "controles": {
        "cn": ["CN1", "CN2"],
        "cp": ["CP1"]
    },
    "comentarios": "Protocolo VR1e2 Biomanguinhos 7500 Real-Time",
    "versao_protocolo": "1.0"
}
```

**Status:** ❌ **NÃO CRIADO AUTOMATICAMENTE**  
**Risco:** Dados incompletos se JSON não existir

---

## 🔄 FLUXO ATUAL DE ADIÇÃO DE EXAME

```
UI (CadastrosDiversosWindow)
└─> _salvar_exame()
    ├─ Lê exames_config.csv  ✅
    ├─ Atualiza entrada em memória
    ├─ Salva exames_config.csv  ✅
    │
    └─ FALTA AQUI:
       ├─ ❌ Atualizar exames_metadata.csv
       ├─ ❌ Atualizar regras_analise_metadata.csv (CRÍTICO!)
       ├─ ❌ Atualizar config.json
       ├─ ❌ Criar config/exams/{slug}.json
       └─ ❌ Recarregar ExamRegistry global
```

---

## 📊 MAPA DE VARIÁVEIS POR LOCAL

| Variável | exames_config | exames_metadata | regras_analise | config.json | config/exams |
|----------|---------------|-----------------|-----------------|-------------|--------------|
| **exame** | ✅ PK | ✅ PK | ✅ PK | ✅ key | ✅ nome_exame |
| **modulo_analise** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **tipo_placa** | ✅ | ✅ | ❌ | ❌ | ✅ (calculated) |
| **numero_kit** | ✅ | ✅ | ❌ | ✅ | ✅ |
| **equipamento** | ✅ | ✅ | ❌ | ❌ | ✅ |
| **CT_RP_MIN** | ❌ | ❌ | ✅ | ❌ | ✅ |
| **CT_RP_MAX** | ❌ | ❌ | ✅ | ❌ | ✅ |
| **CT_DETECTAVEL_MIN** | ❌ | ❌ | ✅ | ❌ | ✅ |
| **CT_DETECTAVEL_MAX** | ❌ | ❌ | ✅ | ❌ | ✅ |
| **CT_INCONCLUSIVO_MIN** | ❌ | ❌ | ✅ | ❌ | ✅ |
| **CT_INCONCLUSIVO_MAX** | ❌ | ❌ | ✅ | ❌ | ✅ |
| **alvos** | ❌ | ❌ | ✅ | ❌ | ✅ |
| **categorias_resultado** | ❌ | ❌ | ✅ | ❌ | ❌ |
| **status_corrida_validos** | ❌ | ❌ | ✅ | ❌ | ❌ |
| **export_fields** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **panel_tests_id** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **controles (CN/CP)** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **mapa_alvos** | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## ⚠️ CENÁRIO: ADICIONAR NOVO EXAME "MPX" (MONKEYPOX)

### Passo 1: User clica "Novo" em CadastrosDiversosWindow

```python
# services/cadastros_diversos.py - _novo_exame()
self.current_exam_id = None
# Limpa campos
```

### Passo 2: User preenche formulário

```
exame: "MPX Teste Kit"
modulo_analise: "analise.mpx.analisar_placa_mpx"
tipo_placa: "96"
numero_kit: "9999"
equipamento: "7500 Real-Time"
```

### Passo 3: User clica "Salvar"

```python
# services/cadastros_diversos.py - _salvar_exame() [Linha 674]

def _salvar_exame(self) -> None:
    rows = self._load_csv("exames")  # ✅ Lê exames_config.csv
    
    dados = {
        "exame": self.entry_exame.get().strip(),           # "MPX Teste Kit"
        "modulo_analise": self.entry_modulo.get().strip(), # "analise.mpx.analisar_placa_mpx"
        "tipo_placa": self.entry_tipo_placa.get().strip(), # "96"
        "numero_kit": self.entry_numero_kit.get().strip(), # "9999"
        "equipamento": self.entry_equipamento_exame.get().strip(), # "7500 Real-Time"
    }
    
    if self.current_exam_id is None:
        rows.append(dados)  # ✅ Adiciona nova linha
    
    self._save_csv("exames", rows)  # ✅ Salva exames_config.csv
    self._carregar_exames()         # ✅ Recarrega Treeview
```

**Resultado Esperado:** `exames_config.csv` tem nova linha  
**Resultado Real:** ✅ OK

---

### ❌ PROBLEMA 1: exames_metadata.csv NÃO é atualizado

**Consequência:**
```
ExamRegistry vai procurar em exames_metadata.csv para dados adicionais
├─ Não encontra "MPX Teste Kit" em exames_metadata.csv
├─ Usa valores defaults de _safe_float()
├─ alvos = [] (VAZIO!)
└─ faixas_ct = defaults genéricos
```

**Problema:** Sem alvos, o histórico não criará colunas dinâmicas para MPX!

---

### ❌ PROBLEMA 2: regras_analise_metadata.csv NÃO é atualizado

**Consequência:**
```
ExamRegistry procura regras para MPX
├─ Não encontra entrada em regras_analise_metadata.csv
├─ alvos = [] (sem nenhum alvo!)
├─ faixas_ct = defaults (provavelmente incorretos!)
├─ Não há valores para CT_RP_MIN, CT_DETECTAVEL_MAX, etc.
└─ Análise não pode executar corretamente!
```

**Variáveis não Sincronizadas:**
- [ ] CT_RP_MIN = ? (Qual deve ser para MPX?)
- [ ] CT_RP_MAX = ? 
- [ ] CT_DETECTAVEL_MIN = ?
- [ ] CT_DETECTAVEL_MAX = ?
- [ ] CT_INCONCLUSIVO_MIN = ?
- [ ] CT_INCONCLUSIVO_MAX = ?
- [ ] alvos = ? (Ex: `DEN1;DEN2;ZIKA;...`)
- [ ] categorias_resultado = ?
- [ ] status_corrida_validos = ?

---

### ❌ PROBLEMA 3: config.json NÃO é atualizado

**Consequência:**
```
"active_exams" não contém "MPX Teste Kit"
├─ UI pode não exibir como opção
├─ Envio GAL pode não reconhecer
└─ Integração com sistema pode falhar
```

---

### ❌ PROBLEMA 4: config/exams/mpx_teste_kit.json NÃO é criado

**Consequência:**
```
JSON de override não existe
├─ ExamRegistry._load_from_json() não encontra nada para sobrescrever
├─ Usa apenas dados do CSV
├─ Sem mapa_alvos, export_fields, panel_tests_id
└─ Envio GAL terá campos incorretos
```

**Variáveis Faltando:**
- [ ] mapa_alvos - Mapping entre alvos e nomes GAL
- [ ] export_fields - Campos para exportar ao GAL
- [ ] panel_tests_id - ID do painel no GAL
- [ ] controles (CN/CP) - Poços de controle

---

### ❌ PROBLEMA 5: ExamRegistry global NÃO é recarregado

**Consequência:**
```
ExamRegistry em memória ainda contém dados antigos
├─ `registry.exams` não contém "MPX Teste Kit"
├─ Análises futuras não encontram o exame
├─ Sistema continua funcionando com dados antigos
└─ Requer restart para carregar novo exame
```

**Solução Necessária:** Após salvar, chamar:
```python
registry.load()  # Recarrega tudo
```

---

## 🎯 RESUMO DE PROBLEMAS

| # | Arquivo | Problema | Impacto | Severidade |
|---|---------|----------|--------|-----------|
| 1 | `exames_metadata.csv` | Não sincronizado | Metadados inconsistentes | 🟡 Médio |
| 2 | `regras_analise_metadata.csv` | Não sincronizado | **Alvos vazios, faixas CT incorretas** | 🔴 **CRÍTICO** |
| 3 | `config.json` | Não sincronizado | Exame não listado em active_exams | 🟡 Médio |
| 4 | `config/exams/{slug}.json` | Não criado | Mapping GAL faltando | 🟡 Médio |
| 5 | `ExamRegistry` global | Não recarregado | Novo exame invisível até restart | 🟡 Médio |
| 6 | **Nenhuma validação** | Dados incompletos | Qualquer exame pode ficar quebrado | 🔴 **CRÍTICO** |
| 7 | **Sem confirmação** | User pode sair sem salvar | Dados perdidos | 🟡 Médio |

---

## 📋 CHECKLIST DE VARIÁVEIS OBRIGATÓRIAS

### Para um novo exame funcionar completamente, precisa de:

**Em exames_config.csv (UI consegue):**
- ✅ `exame` - Nome do exame
- ✅ `modulo_analise` - Path do módulo Python
- ✅ `tipo_placa` - Número de poços (48, 96, 36)
- ✅ `numero_kit` - Kit code
- ✅ `equipamento` - Nome do equipamento

**Em regras_analise_metadata.csv (MANUAL - NÃO TEM UI!):**
- ❌ `alvos` - Alvos separados por `;` (Ex: `DEN1;DEN2;ZIKA`)
- ❌ `CT_RP_MIN` - Limite mínimo para Replicação Positiva
- ❌ `CT_RP_MAX` - Limite máximo para Replicação Positiva
- ❌ `CT_DETECTAVEL_MIN` - Mínimo para "Detectado"
- ❌ `CT_DETECTAVEL_MAX` - Máximo para "Detectado"
- ❌ `CT_INCONCLUSIVO_MIN` - Mínimo para "Inconclusivo"
- ❌ `CT_INCONCLUSIVO_MAX` - Máximo para "Inconclusivo"
- ❌ `categorias_resultado` - Resultados válidos separados por `;`
- ❌ `status_corrida_validos` - Status válidos separados por `;`
- ❌ `observacoes` - Notas

**Em config.json (MANUAL):**
- ❌ Adicionar `exame_name` em `active_exams`
- ❌ Criar `configs[exame_name]` com `kit_codigo` e `export_fields`

**Em config/exams/{slug}.json (MANUAL):**
- ❌ `nome_exame`
- ❌ `slug`
- ❌ `alvos` (lista, não string com `;`)
- ❌ `mapa_alvos` - Mapping para GAL
- ❌ `export_fields` - Campos para exportação
- ❌ `faixas_ct` - Limites de CT
- ❌ `panel_tests_id` - ID no GAL
- ❌ `controles` - CN e CP wells

---

## 💡 RECOMENDAÇÕES

### Curto Prazo (Semana 1):
1. ✏️ Adicionar campos adicionais à UI de `_build_tab_exames()`:
   - CT_RP_MIN, CT_RP_MAX
   - CT_DETECTAVEL_MIN, CT_DETECTAVEL_MAX
   - CT_INCONCLUSIVO_MIN, CT_INCONCLUSIVO_MAX
   - alvos (semicolon-separated)
   - categoria_resultado
   - panel_tests_id

2. 🔄 Modificar `_salvar_exame()` para:
   - Atualizar também `regras_analise_metadata.csv`
   - Atualizar `exames_metadata.csv`
   - Recarregar `ExamRegistry` global

3. ✅ Adicionar validação:
   - Verificar se `alvos` não está vazio
   - Verificar se faixas_ct são válidas
   - Avisar user se dados incompletos

### Médio Prazo (Mês 1):
4. 📁 Criar JSON em `config/exams/{slug}.json` automaticamente

5. 🔄 Atualizar `config.json` via código (não manual)

6. 🔀 Sincronização bidirecional:
   - Se usuário editar JSON, refletir em CSV
   - Se usuário editar CSV, refletir em JSON

### Longo Prazo (Trimestre 1):
7. 🗄️ Migrar para SQLite (eliminar vários CSVs)

8. 🤖 Criar módulo `ExamManager` dedicado

---

## 📝 CONCLUSÃO

**O mecanismo de inclusão de exames está INCOMPLETO.**

Quando um novo exame é adicionado via UI, apenas `exames_config.csv` é atualizado. Faltam **11 variáveis críticas** em `regras_analise_metadata.csv`, e vários arquivos não são sincronizados.

**Recomendação:** Antes de adicionar novo exame em produção:
1. Adicionar manualmente entrada em `regras_analise_metadata.csv`
2. Criar `config/exams/{slug}.json` com dados completos
3. Atualizar `config.json` com novo exame em `active_exams`

Sem isso, o novo exame **funcionará parcialmente** (será reconhecido mas sem alvos, com faixas CT incorretas, sem mapping GAL).

---

**Data:** 2025-12-07  
**Status:** ⚠️ **CRÍTICO** - Necessita implementação urgente
