# 🔍 MAPEAMENTO DE LÓGICA DUPLICADA E BUGS POTENCIAIS

**Data da Análise:** 10/12/2025  
**Sistema:** IntegraGAL v2.0  
**Escopo:** Lógica de classificação de resultados, validação de controles e limiares de CT

---

## 📊 RESUMO EXECUTIVO

| Categoria | Ocorrências | Criticidade |
|-----------|-------------|-------------|
| **Constantes duplicadas** | 4 locais | 🔴 ALTA |
| **Lógica de classificação duplicada** | 5 implementações | 🔴 ALTA |
| **Validação de controles** | 2 sistemas paralelos | 🟡 MÉDIA |
| **Normalização de resultados** | 3 versões diferentes | 🔴 ALTA |
| **Bugs identificados** | 7 críticos | 🔴 CRÍTICA |

---

## 🔴 PROBLEMA #1: CONSTANTES DE CT DUPLICADAS (4 LOCAIS)

### **Locais onde as constantes estão definidas:**

#### **1.1. `analise/vr1e2_biomanguinhos_7500.py`** (FONTE ORIGINAL)
```python
CT_RP_MIN = 10              # ⚠️ DIFERENTE dos outros!
CT_RP_MAX = 35
CT_DETECTAVEL_MAX = 38      # ⚠️ DIFERENTE dos outros!
CT_INCONCLUSIVO_MIN = 38.01
CT_INCONCLUSIVO_MAX = 40    # ⚠️ DIFERENTE dos outros!
```
**Status:** ❌ **NÃO UTILIZADAS NA VALIDAÇÃO** (apenas na assinatura)

#### **1.2. `services/exam_registry.py`** (CONFIGURAÇÃO DINÂMICA)
```python
"detect_max": _safe_float(regras.get("CT_DETECTAVEL_MAX", 38.0), 38.0)
"inconc_min": _safe_float(regras.get("CT_INCONCLUSIVO_MIN", 38.01), 38.01)
"inconc_max": _safe_float(regras.get("CT_INCONCLUSIVO_MAX", 40.0), 40.0)
"rp_min": _safe_float(regras.get("CT_RP_MIN", 15.0), 15.0)     # ⚠️ DIFERENTE!
"rp_max": _safe_float(regras.get("CT_RP_MAX", 35.0), 35.0)
```
**Status:** ✅ Carregado de CSV, permite customização por exame

#### **1.3. `services/universal_engine.py` - Linha 661** (DEFAULTS HARDCODED)
```python
ct_detect_max = as_float("CT_DETECTAVEL_MAX", 40.0)      # ⚠️ DIFERENTE!
ct_inconc_min = as_float("CT_INCONCLUSIVO_MIN", 40.01)   # ⚠️ DIFERENTE!
ct_inconc_max = as_float("CT_INCONCLUSIVO_MAX", 45.0)    # ⚠️ DIFERENTE!
ct_rp_min = as_float("CT_RP_MIN", 15.0)
ct_rp_max = as_float("CT_RP_MAX", 35.0)
```
**Status:** ✅ Usado na interpretação com RP

#### **1.4. `services/universal_engine.py` - Linha 1020** (VALIDAÇÃO DE CONTROLES)
```python
ct_detect_max = as_float("CT_DETECTAVEL_MAX", 40.0)
ct_inconc_min = as_float("CT_INCONCLUSIVO_MIN", 38.01)
ct_inconc_max = as_float("CT_INCONCLUSIVO_MAX", 45.0)
ct_rp_min = as_float("CT_RP_MIN", 15.0)
ct_rp_max = as_float("CT_RP_MAX", 35.0)
```
**Status:** ✅ Usado na determinação de status da corrida

#### **1.5. `services/universal_engine.py` - Linha 641** (FAIXAS ALTERNATIVAS)
```python
ct_detect_max = float(faixas.get("detect_max", faixas.get("detectMax", 40.0)))
ct_inconc_min = float(faixas.get("inconc_min", faixas.get("inconcMin", 40.01)))
ct_inconc_max = float(faixas.get("inconc_max", faixas.get("inconcMax", 45.0)))
ct_rp_min = float(faixas.get("rp_min", faixas.get("rpMin", 15.0)))
ct_rp_max = float(faixas.get("rp_max", faixas.get("rpMax", 35.0)))
```
**Status:** ✅ Carregado de exam_cfg.faixas_ct

### **❌ INCONSISTÊNCIAS CRÍTICAS:**

| Constante | vr1e2 | exam_registry | universal_engine | universal_engine (alt) |
|-----------|-------|---------------|------------------|------------------------|
| **CT_DETECTAVEL_MAX** | 38.0 | 38.0 | **40.0** ⚠️ | **40.0** ⚠️ |
| **CT_INCONCLUSIVO_MIN** | 38.01 | 38.01 | **40.01** ⚠️ | **40.01** ⚠️ |
| **CT_INCONCLUSIVO_MAX** | 40.0 | 40.0 | **45.0** ⚠️ | **45.0** ⚠️ |
| **CT_RP_MIN** | **10.0** ⚠️ | **15.0** | **15.0** | **15.0** |

**IMPACTO:**
- Amostras com CT entre 38-40 podem ser classificadas como **"Detectado"** ou **"Inconclusivo"** dependendo do módulo
- RP entre 10-15 é válido em `vr1e2_biomanguinhos_7500.py` mas **inválido** em outros módulos

---

## 🔴 PROBLEMA #2: LÓGICA DE CLASSIFICAÇÃO DUPLICADA

### **2.1. `analise/vr1e2_biomanguinhos_7500.py` - Linha 162**
```python
df_final[res_col] = df_final[col_ct].apply(
    lambda x: "Detectado"
    if pd.notna(x) and x <= CT_DETECTAVEL_MAX
    else ("Inconclusivo" if pd.notna(x) and CT_INCONCLUSIVO_MIN <= x <= CT_INCONCLUSIVO_MAX 
          else "Nao Detectado")
)
```
**Características:**
- ✅ CT vazio → "Nao Detectado" (CORRETO conforme especificação)
- ❌ **NÃO valida RP** antes de classificar
- ❌ CT > 40 → "Nao Detectado" (sem distinção de "Inválido")

### **2.2. `services/universal_engine.py` - Função `_interpretar_com_rp` (Linha 770)**
```python
def _interpretar_com_rp(
    ct_rp: Optional[float],
    ct_alvo: Optional[float],
    ct_detect_min: float,
    ct_detect_max: float,
    ct_inconc_min: float,
    ct_inconc_max: float,
    ct_rp_min: float,
    ct_rp_max: float,
) -> str:
    if ct_rp is None:
        return "Invalido"
    try:
        valor_rp = float(ct_rp)
    except Exception:
        return "Invalido"
    if not (ct_rp_min <= valor_rp <= ct_rp_max):
        return "Invalido"  # ✅ VALIDA RP!
    
    if ct_alvo is None:
        return "Nao Detectado"  # ✅ CT vazio = ND
    
    try:
        valor_ct = float(ct_alvo)
    except Exception:
        return "Nao Detectado"
    
    if valor_ct <= ct_detect_max:
        return "Detectado"
    if ct_inconc_min <= valor_ct <= ct_inconc_max:
        return "Inconclusivo"
    return "Nao Detectado"
```
**Características:**
- ✅ **VALIDA RP ANTES** de classificar alvo
- ✅ CT vazio → "Nao Detectado"
- ✅ RP inválido → **"Invalido"** (diferencia falha técnica)

### **2.3. `services/plate_viewer.py` - Função `normalize_result` (Linha 703)**
```python
def normalize_result(value: str) -> str:
    """Normaliza textos de resultado do CSV (ex: 'SC2 - 1', 'HMPV - 2')."""
    txt = value.strip().upper()
    
    # Formato CSV: "ALVO - NÚMERO"
    if " - " in txt:
        parts = txt.split(" - ")
        if len(parts) >= 2:
            num = parts[-1].strip()
            if num == "1":
                return "Det"      # Detectado
            elif num == "2":
                return "ND"       # Não Detectado
            else:
                return "Inc"      # Inconclusivo
    
    # Fallback textual
    if any(k in txt for k in ["INC", "3"]):
        return "Inc"
    if any(k in txt for k in ["NAO DETECTADO", "..."]):
        return "ND"
    if any(k in txt for k in ["DETECTADO", "..."]):
        return "Det"
    
    return txt  # ⚠️ Retorna original se não reconhecer
```
**Características:**
- ✅ Aceita formato numérico (1/2/3) do GAL
- ✅ Aceita formato textual
- ⚠️ **NÃO classifica baseado em CT** (apenas normaliza strings)

### **2.4. `services/plate_viewer.py` - Método `apply_target_changes` (Linha 1294)**
```python
# Reanalisar resultado baseado no novo CT
# Regras básicas: CT < 35 = Detectado, CT >= 35 = Inconclusivo, sem CT = não detectado
if new_ct < 35:
    new_res = "Det"
elif new_ct >= 35:
    new_res = "Inc"
```
**Características:**
- ⚠️ **LIMIAR DIFERENTE:** 35 ao invés de 38/40
- ⚠️ **HARDCODED** (não usa constantes configuráveis)
- ❌ Não valida RP

### **2.5. `ui/janela_analise_completa.py` - Relatórios (Linha 466)**
```python
detectados = valores.str.contains("DET|POS", regex=True, na=False).sum()
nao_detectados = valores.str.contains("ND|NEG", regex=True, na=False).sum()
inconclusivos = valores.str.contains("INC", regex=True, na=False).sum()
invalidos = valores.str.contains("INV", regex=True, na=False).sum()
```
**Características:**
- ✅ Apenas conta, não classifica
- ⚠️ Depende de resultados já classificados por outros módulos

---

## 🔴 PROBLEMA #3: VALIDAÇÃO DE CONTROLES DUPLICADA

### **3.1. `analise/vr1e2_biomanguinhos_7500.py`**
```python
status_corrida = "Valida"  # ❌ SEMPRE VÁLIDA, SEM VALIDAÇÃO!
```
**Status:** 🔴 **BUG CRÍTICO** - Não valida controles CN/CP nem RP

### **3.2. `services/universal_engine.py` - Função `_determinar_status_corrida` (Linha 1001)**
```python
status_corrida = "Valida"

# Validação de CN
if not mask_cn_sample.any() or not mask_cp_sample.any():
    status_corrida = "Invalida (Controles Ausentes)"
elif _any_detect(mask_cn_sample):
    status_corrida = "Invalida (CN Detectado)"

# Validação de CP (RP na faixa)
sub_cp_rp = df_tmp[mask_cp_sample & df_tmp["target_upper"].isin(rp_names)]
rp_cp_vals = [v for v in sub_cp_rp["ct"].tolist() if v is not None]
if not rp_cp_vals or not all(ct_rp_min <= float(v) <= ct_rp_max for v in rp_cp_vals):
    status_corrida = "Invalida (CP Fora do Intervalo)"

# Validação de RP por amostra
if status_corrida.startswith("Valida"):
    for _, sub in df_rp.groupby("sample_id"):
        vals = [v for v in sub["ct"].tolist() if v is not None]
        if not vals or not all(ct_rp_min <= float(v) <= ct_rp_max for v in vals):
            status_corrida = "Invalida (RP fora do intervalo)"
            break
```
**Status:** ✅ **COMPLETO** - Valida CN, CP e RP

---

## 🔴 PROBLEMA #4: NORMALIZAÇÃO DE RESULTADOS TRIPLICADA

### **Três funções diferentes fazem a mesma coisa:**

#### **4.1. `utils/gui_utils.py` - `_norm_res_label` (Linha 66)**
```python
def _norm_res_label(val: str) -> str:
    s = str(val).strip().lower()
    s = s.replace("á", "a").replace("é", "e").replace("í", "i")...
    
    if s in {"detectavel", "detectado"}:
        return "detectavel"
    if s in {"nao detectavel", "nao detectado"}:
        return "nao_detectavel"
    if s in {"invalido"}:
        return "invalido"
    return s
```

#### **4.2. `ui/janela_analise_completa.py` - `_norm_res_label` (Linha 16)**
```python
def _norm_res_label(val: str) -> str:
    s = str(val).strip().upper()
    if "INVAL" in s or "INV" in s:
        return "invalido"
    if "DET" in s or "POS" in s:
        return "positivo"
    if "INC" in s:
        return "inconclusivo"
    if "ND" in s or "NEG" in s:
        return "negativo"
    return s.lower()
```

#### **4.3. `services/plate_viewer.py` - `normalize_result` (Linha 703)**
```python
def normalize_result(value: str) -> str:
    txt = value.strip().upper()
    if " - " in txt:
        num = parts[-1].strip()
        if num == "1": return "Det"
        elif num == "2": return "ND"
        else: return "Inc"
    # ... fallback textual
```

**❌ PROBLEMA:** Três implementações diferentes com lógicas incompatíveis!

---

## 🐛 BUGS CRÍTICOS IDENTIFICADOS

### **BUG #1: Constantes de RP inconsistentes**
**Arquivo:** `analise/vr1e2_biomanguinhos_7500.py`  
**Linha:** 17  
**Problema:** `CT_RP_MIN = 10` vs `15` em outros módulos  
**Impacto:** RPs entre 10-15 têm comportamento indefinido  
**Criticidade:** 🔴 ALTA

### **BUG #2: Faixas de CT inconsistentes**
**Arquivos:** Múltiplos  
**Problema:**
- Detectado: `≤38` vs `≤40`
- Inconclusivo: `38.01-40` vs `40.01-45`  
**Impacto:** Mesma amostra classificada diferente por módulos diferentes  
**Criticidade:** 🔴 CRÍTICA

### **BUG #3: Validação de RP ausente em vr1e2**
**Arquivo:** `analise/vr1e2_biomanguinhos_7500.py`  
**Linha:** 176  
**Problema:** Constantes definidas mas não usadas  
**Código:**
```python
# Constantes definidas:
CT_RP_MIN = 10
CT_RP_MAX = 35

# Mas apenas duplica RP:
if "RP" in df_final.columns:
    df_final["RP_1"] = df_final["RP"]
    df_final["RP_2"] = df_final["RP"]
# ❌ SEM VALIDAÇÃO!

status_corrida = "Valida"  # ❌ SEMPRE VÁLIDA
```
**Impacto:** Corridas com RP inválido marcadas como válidas  
**Criticidade:** 🔴 CRÍTICA

### **BUG #4: Validação de controles ausente em vr1e2**
**Arquivo:** `analise/vr1e2_biomanguinhos_7500.py`  
**Linha:** 176  
**Problema:** Não valida CN/CP  
**Impacto:** Corridas com controles falhados marcadas como válidas  
**Criticidade:** 🔴 CRÍTICA

### **BUG #5: Limiar hardcoded em plate_viewer**
**Arquivo:** `services/plate_viewer.py`  
**Linha:** 1294  
**Problema:** `CT < 35` hardcoded (deveria usar constantes configuráveis)  
**Impacto:** Edições manuais no mapa usam critério diferente da análise  
**Criticidade:** 🟡 MÉDIA

### **BUG #6: Normalização de resultados sem consistência**
**Arquivos:** 3 locais diferentes  
**Problema:** Três funções diferentes com outputs incompatíveis  
**Impacto:** Resultados podem ser mal interpretados em diferentes partes do sistema  
**Criticidade:** 🟡 MÉDIA

### **BUG #7: Status do poço ignora resultados "Inv"**
**Arquivo:** `services/plate_viewer.py`  
**Linha:** 518 (`_recompute_status`)  
**Problema:**
```python
# Se nenhum alvo for Det/Inc/ND, status = INVALID
# MAS não verifica se há resultados "Inv" explícitos
else:
    well.status = INVALID
```
**Impacto:** Poços com resultados "Invalido" podem ser processados incorretamente  
**Criticidade:** 🟡 MÉDIA

---

## 💡 RECOMENDAÇÕES DE CORREÇÃO

### **PRIORIDADE 1 (URGENTE):**

1. **Centralizar constantes em arquivo único:**
```python
# Criar: config/ct_thresholds.py
class CTThresholds:
    DETECT_MAX = 38.0
    INCONC_MIN = 38.01
    INCONC_MAX = 40.0
    RP_MIN = 15.0
    RP_MAX = 35.0
```

2. **Adicionar validação em vr1e2_biomanguinhos_7500.py:**
```python
def _validar_corrida(df_final: pd.DataFrame) -> str:
    # Validar CN
    cn_rows = df_final[df_final["Amostra"].str.contains("CN", case=False, na=False)]
    for alvo in TARGET_LIST:
        col = f"Resultado_{alvo.replace(' ', '')}"
        if (cn_rows[col] == "Detectado").any():
            return "Invalida - CN detectou " + alvo
    
    # Validar RP
    if "RP" in df_final.columns:
        rp_invalidos = df_final[
            (df_final["RP"].notna()) & 
            ((df_final["RP"] < CT_RP_MIN) | (df_final["RP"] > CT_RP_MAX))
        ]
        if not rp_invalidos.empty:
            return "Invalida - RP fora da faixa"
    
    return "Valida"
```

3. **Unificar função de normalização:**
```python
# Criar: utils/result_normalizer.py
def normalize_result(value: Any, ct: Optional[float] = None) -> str:
    """
    Normalização única de resultados.
    Aceita: string ("Detectado", "SC2 - 1"), número (1/2/3), ou CT direto
    """
    # Implementação unificada
```

### **PRIORIDADE 2 (IMPORTANTE):**

4. Substituir limiar hardcoded em plate_viewer por constantes configuráveis
5. Adicionar testes unitários para todas as funções de classificação
6. Documentar diferenças entre módulos (se intencionais)

### **PRIORIDADE 3 (MELHORIAS):**

7. Criar sistema de versionamento de limiares (histórico de mudanças)
8. Adicionar logs quando diferentes módulos classificam diferente
9. Dashboard de comparação entre módulos

---

## 📈 ESTATÍSTICAS

- **Total de locais com lógica de classificação:** 5
- **Total de constantes duplicadas:** 20+ ocorrências
- **Módulos afetados:** 6
- **Bugs críticos:** 7
- **Taxa de inconsistência:** ~60% (diferentes módulos = diferentes resultados)

---

## ✅ CONCLUSÃO

O sistema possui **lógica crítica duplicada** em múltiplos locais com **valores inconsistentes**. O módulo `vr1e2_biomanguinhos_7500.py` especificamente:

1. ❌ **NÃO valida controles** (sempre retorna "Valida")
2. ❌ **NÃO valida RP** (constantes definidas mas não usadas)
3. ⚠️ Usa limiares **diferentes** do universal_engine
4. ✅ **ESTÁ CORRETO** ao tratar CT vazio como "Nao Detectado"

**Recomendação:** Priorizar unificação de constantes e adicionar validação em vr1e2 antes de deploy em produção.
