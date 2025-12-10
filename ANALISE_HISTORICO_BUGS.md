# Análise: Histórico de Análises - Problemas Identificados

**Data:** 10/12/2024  
**Sistema:** IntegRAGal  
**Arquivo Analisado:** `reports/historico_analises_*.csv`  

---

## 🚨 Problemas Críticos Identificados

### **PROBLEMA 1: Campo `arquivo_corrida` Vazio** 🔴

**Localização do Bug:** `ui/menu_handler.py` linha 282-295

**Descrição:**
Ao chamar `TabelaComSelecaoSimulada`, **NÃO está passando** os parâmetros necessários:
- `exame`
- `lote`  
- `arquivo_corrida` ❌ **FALTANDO**

**Código Atual (INCORRETO):**
```python
# ui/menu_handler.py linha 282-295
TabelaComSelecaoSimulada(
    self.main_window,
    df,
    status_corrida,
    num_placa,
    data_placa_formatada,
    agravos,
    usuario_logado=getattr(
        self.main_window.app_state, "usuario_logado", "Desconhecido"
    ),
    # ❌ FALTAM: exame, lote, arquivo_corrida
)
```

**Código Esperado (CORRETO):**
```python
# ui/menu_handler.py linha 282-295
TabelaComSelecaoSimulada(
    self.main_window,
    df,
    status_corrida,
    num_placa,
    data_placa_formatada,
    agravos,
    usuario_logado=getattr(
        self.main_window.app_state, "usuario_logado", "Desconhecido"
    ),
    exame=getattr(self.main_window.app_state, "exame_selecionado", ""),
    lote=getattr(self.main_window.app_state, "lote", ""),
    arquivo_corrida=getattr(self.main_window.app_state, "caminho_arquivo_corrida", ""),
)
```

**Impacto:**
- ❌ Coluna `arquivo_corrida` **sempre vazia** no CSV histórico
- ❌ Coluna `exame` **sempre vazia** no CSV histórico
- ❌ Coluna `lote` **sempre vazia** no CSV histórico
- ❌ Impossível rastrear origem dos dados

---

### **PROBLEMA 2: Sistema NÃO Preparado para Múltiplos Exames** 🔴

**Descrição:**
O CSV histórico está recebendo **apenas dados de VR1e2 Biomanguinhos** porque:
1. Sistema **hardcoded** para este exame em vários lugares
2. Alvos são **fixos** (SC2, HMPV, INFA, INFB, ADV, RSV, HRV)
3. Não há **detecção automática** de alvos por exame

**Evidência no CSV:**
```csv
# Colunas hardcoded para VR1e2:
SC2 - R;SC2 - CT;HMPV - R;HMPV - CT;INFA - R;INFA - CT;INFB - R;INFB - CT;ADV - R;ADV - CT;RSV - R;RSV - CT;HRV - R;HRV - CT;RP_1 - CT;RP_2 - CT
```

**Para outros exames (ex: ZDC), faltariam colunas:**
- `ZDC - R`, `ZDC - CT` (Zika)
- `DENV - R`, `DENV - CT` (Dengue)
- `CHIKV - R`, `CHIKV - CT` (Chikungunya)

---

## 🔍 Análise Técnica Detalhada

### Fluxo Atual do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│ 1. ANÁLISE (analysis_service.py)                           │
│    - Processa arquivo CSV/Excel                            │
│    - Armazena resultado em app_state                       │
│    - Define app_state.caminho_arquivo_corrida ✅           │
│    - Define app_state.exame_selecionado ✅                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. EXIBIR RESULTADOS (menu_handler.py)                     │
│    - Cria TabelaComSelecaoSimulada                         │
│    - ❌ NÃO passa arquivo_corrida                          │
│    - ❌ NÃO passa exame                                    │
│    - ❌ NÃO passa lote                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. SALVAR HISTÓRICO (gui_utils.py)                         │
│    - self.arquivo_corrida = "" ❌ (não foi passado)        │
│    - self.exame = "" ❌ (não foi passado)                  │
│    - self.lote = "" ❌ (não foi passado)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. GERAR CSV (history_report.py)                           │
│    - Recebe arquivo_corrida="" ❌                          │
│    - Recebe exame="" ❌                                    │
│    - df["arquivo_corrida"] = "" (vazio)                    │
└─────────────────────────────────────────────────────────────┘
```

---

### Como o Sistema DEVERIA Funcionar

#### Passo 1: Análise Armazena Contexto ✅
```python
# services/analysis_service.py linha 1040-1050
# ✅ JÁ FUNCIONA CORRETAMENTE
self.app_state.caminho_arquivo_corrida = Path(resultado.caminho_entrada_resultados).name
self.app_state.exame_selecionado = "VR1e2 Biomanguinhos 7500"
```

#### Passo 2: Menu Handler Passa Contexto ❌
```python
# ui/menu_handler.py linha 282-295
# ❌ ATUALMENTE NÃO PASSA OS DADOS

TabelaComSelecaoSimulada(
    self.main_window,
    df,
    status_corrida,
    num_placa,
    data_placa_formatada,
    agravos,
    usuario_logado=...,
    # FALTAM ESTES 3 PARÂMETROS:
    exame=self.main_window.app_state.exame_selecionado,
    lote=self.main_window.app_state.lote,
    arquivo_corrida=self.main_window.app_state.caminho_arquivo_corrida,
)
```

#### Passo 3: GUI Utils Recebe Contexto ✅
```python
# utils/gui_utils.py linha 67-143
# ✅ ASSINATURA JÁ ESTÁ CORRETA
def __init__(
    self,
    root,
    dataframe,
    status_corrida,
    num_placa,
    data_placa_formatada,
    agravos,
    usuario_logado: str = "Desconhecido",
    exame: str = "",           # ✅ Parâmetro existe
    lote: str = "",            # ✅ Parâmetro existe
    arquivo_corrida: str = "", # ✅ Parâmetro existe
):
    self.exame = exame
    self.lote = lote
    self.arquivo_corrida = arquivo_corrida
```

#### Passo 4: Salvar Usa Contexto ✅
```python
# utils/gui_utils.py linha 350-370
# ✅ JÁ USA CORRETAMENTE (se receber os dados)
gerar_historico_csv(
    df_para_historico,
    exame=getattr(self, "exame", ""),            # ✅ Usa self.exame
    usuario=self.usuario_logado or "Desconhecido",
    lote=getattr(self, "lote", ""),              # ✅ Usa self.lote
    arquivo_corrida=getattr(self, "arquivo_corrida", ""), # ✅ Usa self.arquivo_corrida
    caminho_csv="logs/historico_analises.csv",
)
```

---

## 📊 Design para Múltiplos Exames

### Como o Sistema TEM Capacidade Dinâmica ✅

**O código de `history_report.py` JÁ está preparado para múltiplos exames:**

```python
# services/history_report.py linha 119-400
def gerar_historico_csv(
    df_final: pd.DataFrame,
    exame: str,  # ✅ Parâmetro genérico
    ...
):
    """
    ✅ Suporta QUALQUER exame (VR1e2, ZDC, VR1, VR2, etc.)
    ✅ Gera colunas dinâmicas conforme alvos do exame
    """
    cfg = get_exam_cfg(exame)  # ✅ Busca config do exame no registry
    
    # ✅ Gera colunas dinamicamente baseado em cfg.alvos
    for alvo in cfg.alvos:
        alvo_norm = cfg.normalize_target(alvo)
        col_res = f"Resultado_{alvo_norm}"
        ct_col = _find_ct_col(alvo_norm)
        targets.append((col_res, ct_col))
```

**Exemplo para VR1e2:**
```python
cfg.alvos = ["SC2", "HMPV", "INF A", "INF B", "ADV", "RSV", "HRV"]
# Gera automaticamente:
# - SC2 - R, SC2 - CT
# - HMPV - R, HMPV - CT
# - INFA - R, INFA - CT
# ... etc
```

**Exemplo para ZDC (se estivesse configurado):**
```python
cfg.alvos = ["ZIKV", "DENV", "CHIKV"]
# Geraria automaticamente:
# - ZIKV - R, ZIKV - CT
# - DENV - R, DENV - CT
# - CHIKV - R, CHIKV - CT
```

---

### Estrutura do CSV Histórico (Design Atual)

#### Colunas Fixas (Sempre Presentes):
```csv
id_registro;           # UUID único
data_hora_analise;     # Timestamp
usuario_analise;       # Quem analisou
exame;                 # ❌ VAZIO (deveria ter "VR1e2 Biomanguinhos 7500")
lote;                  # ❌ VAZIO (deveria ter lote do kit)
arquivo_corrida;       # ❌ VAZIO (deveria ter nome do arquivo CSV)
poco;                  # Ex: A1+A2
amostra;               # Ex: 422386149R
codigo;                # Código da amostra
status_corrida;        # Valida/Invalida
status_gal;            # não enviado/enviado/erro
mensagem_gal;          # Mensagem de status
data_hora_envio;       # Quando foi enviado ao GAL
usuario_envio;         # Quem enviou
sucesso_envio;         # True/False
detalhes_envio;        # Resposta do servidor GAL
criado_em;             # Auditoria
atualizado_em;         # Auditoria
```

#### Colunas Dinâmicas (Baseadas no Exame):
```csv
# Para VR1e2:
SC2 - R;SC2 - CT;
HMPV - R;HMPV - CT;
INFA - R;INFA - CT;
INFB - R;INFB - CT;
ADV - R;ADV - CT;
RSV - R;RSV - CT;
HRV - R;HRV - CT;
RP_1 - CT;RP_2 - CT

# Para ZDC (quando implementado):
ZIKV - R;ZIKV - CT;
DENV - R;DENV - CT;
CHIKV - R;CHIKV - CT;
RP - CT
```

---

## ✅ Solução Implementada

### Correção 1: Passar Parâmetros no menu_handler.py

**Arquivo:** `ui/menu_handler.py`  
**Linha:** 282-295

**Mudança:**
```python
# ANTES (INCORRETO):
TabelaComSelecaoSimulada(
    self.main_window,
    df,
    status_corrida,
    num_placa,
    data_placa_formatada,
    agravos,
    usuario_logado=getattr(
        self.main_window.app_state, "usuario_logado", "Desconhecido"
    ),
)

# DEPOIS (CORRETO):
TabelaComSelecaoSimulada(
    self.main_window,
    df,
    status_corrida,
    num_placa,
    data_placa_formatada,
    agravos,
    usuario_logado=getattr(
        self.main_window.app_state, "usuario_logado", "Desconhecido"
    ),
    exame=getattr(self.main_window.app_state, "exame_selecionado", ""),
    lote=getattr(self.main_window.app_state, "lote", ""),
    arquivo_corrida=getattr(self.main_window.app_state, "caminho_arquivo_corrida", ""),
)
```

---

## 📋 Checklist de Verificação

### Após Aplicar Correção:

- [ ] **Teste 1:** Analisar placa VR1e2
  - [ ] Verificar coluna `exame` no CSV = "VR1e2 Biomanguinhos 7500"
  - [ ] Verificar coluna `arquivo_corrida` no CSV = nome do arquivo analisado
  - [ ] Verificar colunas dinâmicas (SC2 - R, SC2 - CT, etc.)

- [ ] **Teste 2:** Analisar placa ZDC (quando disponível)
  - [ ] Verificar coluna `exame` no CSV = "ZDC Biomanguinhos 7500"
  - [ ] Verificar colunas dinâmicas (ZIKV - R, ZIKV - CT, etc.)

- [ ] **Teste 3:** Verificar rastreabilidade
  - [ ] Procurar registro no CSV por `arquivo_corrida`
  - [ ] Filtrar por `exame`
  - [ ] Validar timestamps

---

## 🎯 Resumo Executivo

### Perguntas Respondidas:

**1. Por que `arquivo_corrida` está vazio?**
- ❌ **Bug:** `menu_handler.py` não passa o parâmetro `arquivo_corrida` ao criar `TabelaComSelecaoSimulada`
- ✅ **Solução:** Adicionar linha com `arquivo_corrida=getattr(...)`

**2. Como está desenhado para múltiplos exames?**
- ✅ **Sistema está preparado:** `history_report.py` gera colunas dinamicamente
- ✅ **Baseado em:** `exam_registry` (config JSON de cada exame)
- ✅ **Suporta:** Qualquer exame cadastrado (VR1e2, ZDC, VR1, VR2, etc.)

**3. Estrutura das colunas por exame:**
```
Colunas Fixas (18 campos) → Sempre presentes
+
Colunas Dinâmicas → cfg.alvos × 2 (Resultado + CT)
+
Colunas RP → cfg.rps (CT dos controles)
```

### Próximas Ações:

1. ✅ **Aplicar correção no `menu_handler.py`** (3 linhas)
2. 🔲 **Testar com VR1e2** (verificar campos preenchidos)
3. 🔲 **Testar com ZDC** (quando disponível)
4. 🔲 **Validar rastreabilidade** (buscar por arquivo_corrida no CSV)

---

**Status:** ✅ **SOLUÇÃO IDENTIFICADA E PRONTA PARA IMPLEMENTAR**
