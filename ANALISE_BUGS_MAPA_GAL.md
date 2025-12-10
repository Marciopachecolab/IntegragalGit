# 🐛 ANÁLISE: Perda de Resultados no Mapa e VSR não exportado

**Data:** 10/12/2025  
**Problemas Reportados:**
1. Após salvar alterações no mapa, **todos os resultados ficam NaN**
2. **VSR (Vírus Sincicial Respiratório)** não está sendo exportado para CSV do GAL

---

## 🔍 PROBLEMA #1: Resultados viram NaN após salvar mapa

### **Causa Raiz Identificada:**

O `PlateModel.to_dataframe()` está retornando **APENAS** as colunas que existem no mapa:
- `Poco`, `Amostra`, `Codigo`
- `Resultado_<ALVO>`, `CT_<ALVO>` para alvos **ativos no mapa**

**MAS** o DataFrame original (`df_analise`) tem **colunas adicionais** que NÃO estão no PlateModel:
- `Status_Corrida`
- Potencialmente outras colunas de metadados

### **Fluxo do Bug:**

```
1. df_analise original:
   - Poco, Amostra, Codigo
   - Resultado_SC2, CT_SC2
   - Resultado_HMPV, CT_HMPV
   - ... (todos os alvos)
   - Status_Corrida (❌ NÃO está no PlateModel)

2. PlateModel.to_dataframe() retorna:
   - Poco, Amostra, Codigo
   - Resultado_SC2, CT_SC2
   - Resultado_HMPV, CT_HMPV
   - ... (apenas alvos presentes)
   - ❌ SEM Status_Corrida

3. _on_mapa_salvo() faz merge:
   colunas_preservar = [c for c in colunas_originais if c not in colunas_do_mapa]
   
   Se colunas_preservar contém colunas que não existem no df_updated:
   - Merge cria NaN para linhas que não têm match perfeito
   - Resultado: TODAS as colunas de resultado ficam NaN!
```

### **Código Problemático:**

**`ui/janela_analise_completa.py` - Linha 390-410:**
```python
# Manter colunas que NÃO vieram do mapa
colunas_do_mapa = set(df_updated.columns)
colunas_preservar = [c for c in colunas_originais if c not in colunas_do_mapa and c != "Selecionado"]

if colunas_preservar:
    df_preservado = self.df_analise[[chave_merge] + colunas_preservar].copy()
    # ❌ PROBLEMA: Merge pode criar NaN se estrutura mudar
    self.df_analise = df_updated.merge(df_preservado, on=chave_merge, how="left")
```

### **Por que os resultados ficam NaN:**

O merge `df_updated.merge(df_preservado)` **sobrescreve** as colunas de resultado de `df_updated` quando há conflito de nomes!

**Exemplo:**
```python
df_updated:
  Poco        Resultado_SC2
  A01+A02     Det

df_preservado:
  Poco        Status_Corrida
  A01+A02     Valida

# Merge:
df_updated.merge(df_preservado, on="Poco")
# Resultado: colunas de df_updated são preservadas
# MAS se há alguma inconsistência na chave, pode criar NaN
```

**PROBLEMA REAL:** O merge está usando `how="left"` mas se a chave não bater **exatamente** (ex: `A01+A02` vs `A01 + A02` com espaços), cria NaN!

---

## 🔍 PROBLEMA #2: VSR não exportado para GAL

### **Causa Raiz:**

O sistema usa **duas nomenclaturas diferentes** para VSR:
1. **Nome interno:** `RSV` (Respiratory Syncytial Virus)
2. **Nome GAL:** `vsincicialresp` (vírus sincicial respiratório)

### **Mapeamento atual em `gal_formatter.py`:**

```python
aliases = {
    "INFLUENZAA": "INF A",
    "INFLUENZAB": "INF B",
    "ADENOVIRUS": "ADV",
    "METAPNEUMOVIRUS": "HMPV",
    "RINOVIRUS": "HRV",
    "SARS-COV-2": "SC2",
    "CORONAVIRUSNCOV": "SC2",
    # ❌ FALTANDO: "VSINCICIALRESP": "RSV"
}
```

### **Fluxo do Bug:**

```
1. DataFrame tem coluna: Resultado_RSV
2. GAL export_fields contém: "vsincicialresp"
3. _find_result_col("vsincicialresp") busca:
   - Normaliza: "VSINCICIALRESP"
   - ❌ NÃO encontra em aliases
   - ❌ NÃO encontra coluna "Resultado_VSINCICIALRESP"
   - Retorna None
4. Resultado: coluna "vsincicialresp" fica VAZIA no CSV GAL
```

### **Evidência nos logs:**

Nos CSVs gerados em `reports/`:
```csv
# gal_20251205T075054Z_exame.csv
...resultado_rsv...  # ✅ RSV aparece aqui (formato antigo)

# gal_20251205T233305Z_exame.csv  
...vsincicialresp...  # ❌ Coluna existe mas está VAZIA
```

### **Outros alvos potencialmente afetados:**

Verificando `export_fields` default:
```python
export_fields = [
    "Influenzaa",      # ✅ Mapeado
    "influenzab",      # ✅ Mapeado
    "coronavirusncov", # ✅ Mapeado
    "adenovirus",      # ✅ Mapeado
    "vsincicialresp",  # ❌ NÃO mapeado → BUG!
    "metapneumovirus", # ✅ Mapeado
    "rinovirus",       # ✅ Mapeado
]
```

**Apenas VSR está sem alias!**

---

## 💡 SOLUÇÕES

### **SOLUÇÃO #1: Fix perda de resultados no mapa**

**Opção A - Validação de chave de merge (RECOMENDADO):**
```python
def _on_mapa_salvo(self, plate_model: PlateModel):
    # ... código existente ...
    
    if chave_merge:
        # ✅ NORMALIZAR CHAVES ANTES DO MERGE
        df_updated[chave_merge] = df_updated[chave_merge].str.strip()
        self.df_analise[chave_merge] = self.df_analise[chave_merge].str.strip()
        
        # Merge com validação
        df_merged = df_updated.merge(
            self.df_analise[[chave_merge, "Selecionado"] + colunas_preservar],
            on=chave_merge,
            how="left",
            suffixes=('', '_OLD')  # Evitar sobrescrever
        )
        
        # Remover colunas duplicadas
        df_merged = df_merged[[c for c in df_merged.columns if not c.endswith('_OLD')]]
```

**Opção B - Atualização seletiva (MAIS SEGURO):**
```python
def _on_mapa_salvo(self, plate_model: PlateModel):
    df_updated = plate_model.to_dataframe()
    
    # ✅ ATUALIZAR APENAS COLUNAS QUE VIERAM DO MAPA
    for col in df_updated.columns:
        if col in self.df_analise.columns and col != chave_merge:
            # Atualizar coluna existente por índice de merge
            self.df_analise.update(
                df_updated.set_index(chave_merge)[col].to_frame()
            )
```

### **SOLUÇÃO #2: Fix VSR não exportado**

**Adicionar alias em `gal_formatter.py`:**
```python
aliases = {
    "INFLUENZAA": "INF A",
    "INFLUENZAB": "INF B",
    "ADENOVIRUS": "ADV",
    "ADENOVÍRUS": "ADV",
    "METAPNEUMOVIRUS": "HMPV",
    "RINOVIRUS": "HRV",
    "RINOVÍRUS": "HRV",
    "SARS-COV-2": "SC2",
    "SARSCOV2": "SC2",
    "CORONAVIRUSNCOV": "SC2",
    # ✅ ADICIONAR:
    "VSINCICIALRESP": "RSV",
    "VSINCICIALRESPA": "RSV",  # Variante A
    "VSINCICIALRESPB": "RSV",  # Variante B
}
```

---

## 📊 PRIORIDADE DE CORREÇÃO

| Bug | Impacto | Criticidade | Complexidade |
|-----|---------|-------------|--------------|
| **Resultados → NaN** | 🔴 CRÍTICO | **URGENTE** | MÉDIA |
| **VSR não exporta** | 🟡 ALTO | IMPORTANTE | BAIXA |

---

## ✅ TESTE APÓS CORREÇÃO

### **Teste #1: Mapa → Análise**
1. Abrir análise com resultados válidos
2. Ir para mapa da placa
3. Alterar um CT
4. Clicar "Aplicar"
5. Clicar "Salvar e Voltar"
6. **✅ Verificar:** Resultados continuam preenchidos (não NaN)

### **Teste #2: Exportação VSR**
1. Processar corrida com VSR detectado
2. Salvar CSV para GAL
3. **✅ Verificar:** Coluna `vsincicialresp` preenchida com "1" (detectado)
4. **✅ Verificar:** Arquivo GAL contém resultados corretos

---

## 🔧 IMPLEMENTAÇÃO

Próximo passo: Implementar correções em:
1. `ui/janela_analise_completa.py` - Método `_on_mapa_salvo`
2. `exportacao/gal_formatter.py` - Dicionário `aliases`
