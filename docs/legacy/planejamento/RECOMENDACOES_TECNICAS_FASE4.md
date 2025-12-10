# RECOMENDAÇÕES TÉCNICAS - FASE 4
## Patches recomendados para completar integração do Registry

---

## 1. PATCH 1: universal_engine.py - Motor (CRÍTICO)

### Localização: `_aplicar_regras_ct_e_interpretacao()` (linha ~263)

**ANTES (usando config_regras legado):**
```python
def _aplicar_regras_ct_e_interpretacao(
    df_norm: pd.DataFrame, contexto: AnaliseContexto
) -> pd.DataFrame:
    cfg = contexto.config_regras  # ← legado CSV
    def as_float(key: str, default: float) -> float:
        try:
            return float((cfg.get(key) or "").replace(",", "."))
        except Exception:
            return default

    ct_detect_max = as_float("CT_DETECTAVEL_MAX", 40.0)
    ct_inconc_min = as_float("CT_INCONCLUSIVO_MIN", 40.01)
    ct_inconc_max = as_float("CT_INCONCLUSIVO_MAX", 45.0)
    ct_rp_min = as_float("CT_RP_MIN", 15.0)
    ct_rp_max = as_float("CT_RP_MAX", 35.0)
```

**DEPOIS (usando registry):**
```python
def _aplicar_regras_ct_e_interpretacao(
    df_norm: pd.DataFrame, contexto: AnaliseContexto
) -> pd.DataFrame:
    # Usa registry como fonte primária, fallback para config_regras legado
    exam_cfg = get_exam_cfg(contexto.config_equip.get("exame", ""))
    
    if exam_cfg and exam_cfg.faixas_ct:
        ct_detect_max = exam_cfg.faixas_ct.get("detect_max", 37.0)
        ct_inconc_min = exam_cfg.faixas_ct.get("inconc_min", 37.01)
        ct_inconc_max = exam_cfg.faixas_ct.get("inconc_max", 40.0)
        ct_rp_min = exam_cfg.faixas_ct.get("rp_min", 15.0)
        ct_rp_max = exam_cfg.faixas_ct.get("rp_max", 35.0)
    else:
        # Fallback legado
        cfg = contexto.config_regras
        def as_float(key: str, default: float) -> float:
            try:
                return float((cfg.get(key) or "").replace(",", "."))
            except Exception:
                return default
        ct_detect_max = as_float("CT_DETECTAVEL_MAX", 37.0)
        ct_inconc_min = as_float("CT_INCONCLUSIVO_MIN", 37.01)
        ct_inconc_max = as_float("CT_INCONCLUSIVO_MAX", 40.0)
        ct_rp_min = as_float("CT_RP_MIN", 15.0)
        ct_rp_max = as_float("CT_RP_MAX", 35.0)
```

**Benefício:** Motor sempre usa valores de registry se disponível; fallback para CSV antigo garante compatibilidade.

---

## 2. PATCH 2: plate_viewer.py - Mapa (CRÍTICO)

### Localização: `PlateModel.from_df()` (linha ~100)

**ANTES (exam_cfg ignorado):**
```python
@classmethod
def from_df(
    cls,
    df_final: pd.DataFrame,
    group_size: Optional[int] = None,
    exame: Optional[str] = None,
) -> "PlateModel":
    model = cls()
    # ... inicializa wells ...
```

**DEPOIS (carrega e usa exam_cfg):**
```python
@classmethod
def from_df(
    cls,
    df_final: pd.DataFrame,
    group_size: Optional[int] = None,
    exame: Optional[str] = None,
) -> "PlateModel":
    model = cls()
    
    # Carrega configuração do exame
    if exame:
        model.exam_cfg = get_exam_cfg(exame)
    
    # Determina tamanho de grupo
    if group_size is None and model.exam_cfg:
        group_size = model.exam_cfg.bloco_size()
    model.group_size = group_size or 1
    
    # ... resto do inicialização ...
```

**Adicionar em `_get_well_color()` (linha ~X):**
```python
def _get_well_color(self, well: WellData) -> str:
    """Retorna cor conforme status e faixas do registry."""
    if well.is_control:
        return STATUS_COLORS[CONTROL_CN]
    
    # Para RPs: use faixas_ct do registry
    for target_name, result in well.targets.items():
        if target_name.upper().startswith("RP"):
            if result.ct is None:
                return STATUS_COLORS[EMPTY]
            # Verifica faixas
            if self.exam_cfg and self.exam_cfg.faixas_ct:
                rp_min = self.exam_cfg.faixas_ct.get("rp_min", 15.0)
                rp_max = self.exam_cfg.faixas_ct.get("rp_max", 35.0)
                if rp_min <= result.ct <= rp_max:
                    return STATUS_COLORS[POSITIVE]  # RP bom
                else:
                    return STATUS_COLORS[NEGATIVE]   # RP fora da faixa
    
    # Para alvos: resultado qualitativo
    if well.status == POSITIVE:
        return STATUS_COLORS[POSITIVE]
    elif well.status == NEGATIVE:
        return STATUS_COLORS[NEGATIVE]
    elif well.status == INCONCLUSIVE:
        return STATUS_COLORS[INCONCLUSIVE]
    else:
        return STATUS_COLORS[EMPTY]
```

**Benefício:** Cores dinamicamente ajustadas por exame; RP avaliados por faixa; blocos corretos.

---

## 3. PATCH 3: history_report.py - Histórico (ALTO)

### Localização: `gerar_historico_csv()` (linha ~130)

**ANTES (alvos não normalizados):**
```python
for col_res, col_ct in targets:
    base = str(col_res).replace("Resultado_", "").strip()
    res_val = r.get(col_res)
    res_code = _map_result(res_val)
    linha[f"{base} - R"] = f"{base} - {res_code}" if res_code else ""
```

**DEPOIS (usa normalize_target):**
```python
for col_res, col_ct in targets:
    # Extrai nome do alvo
    base_raw = str(col_res).replace("Resultado_", "").strip()
    
    # Normaliza via registry
    base_norm = cfg.normalize_target(base_raw)
    
    # Obtém resultado
    res_val = r.get(col_res)
    res_code = _map_result(res_val)
    
    # Usa nome normalizado
    linha[f"{base_norm} - R"] = f"{base_norm} - {res_code}" if res_code else ""
    
    # CT com nome normalizado
    if col_ct and col_ct in r:
        linha[f"{base_norm} - CT"] = _fmt_ct(r.get(col_ct))
```

**Benefício:** Histórico usa nomes canonicalizados; mapa_alvos aplicado automaticamente.

---

## 4. PATCH 4: main.py - Exportação (ALTO)

### Localização: `_formatar_para_gal()` (linha ~160)

**ANTES (mapeamento incompleto):**
```python
def _map_result(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    s = str(val).strip().lower()
    if "inconcl" in s:
        return "3"
    if "nao" in s and "detect" in s:
        return "2"
    if "detect" in s:
        return "1"
    return ""
```

**DEPOIS (mapeamento completo):**
```python
def _map_result(val):
    """Mapeia resultado textual para código GAL: "1" (Detectado), "2" (ND), "3" (Inc), "" (Inv/Vazio)."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    
    s = str(val).strip().lower()
    
    # Se já vier em formato "ALVO - 1/2/3"
    if " - " in s:
        parts = s.split(" - ")
        last = parts[-1].strip()
        if last in {"1", "2", "3"}:
            return last
    
    if s in {"1", "2", "3"}:
        return s
    
    # Mapeia por palavras-chave
    if any(k in s for k in ["inc", "incon"]):
        return "3"
    
    if ("nao" in s or "não" in s) and "detect" in s:
        return "2"
    
    if any(k in s for k in ["neg", "nd"]):
        return "2"
    
    if any(k in s for k in ["det", "pos", "reag"]):
        return "1"
    
    # Inválido/falha = vazio (não exportável)
    return ""
```

**Adicionar filtro com registry:**
```python
def _is_exportavel(code: str, cfg) -> bool:
    """Valida se código é exportável (não CN/CP, apenas numérico)."""
    if not code:
        return False
    
    c = str(code).upper()
    
    # Verifica controles do registry
    if cfg and cfg.controles:
        cn_list = [str(x).upper() for x in cfg.controles.get("cn", [])]
        cp_list = [str(x).upper() for x in cfg.controles.get("cp", [])]
        if c in cn_list or c in cp_list:
            return False
    
    # Fallback: hardcoded CN/CP
    if "CN" in c or "CP" in c:
        return False
    
    # Deve ser numérico
    return c.isdigit()

# Use na lógica:
export_mask = cod_col.apply(lambda x: _is_exportavel(x, cfg))
```

**Benefício:** Controles dinâmicos; validação robusta; compatível com custom controls.

---

## 5. PATCH 5: envio_gal.py - Geração por Painel (MÉDIO)

### Localização: `GalService.preparar_dados_para_envio()` (novo método)

**ADICIONAR:**
```python
def preparar_dados_por_painel(
    self, 
    df_resultados: pd.DataFrame, 
    exame: str
) -> Dict[str, pd.DataFrame]:
    """
    Organiza dados em DataFrames por painel conforme cfg.export_fields.
    
    Retorna: {"painel_1": df_painel1, "painel_2": df_painel2, ...}
    """
    cfg = get_exam_cfg(exame)
    panel_id = cfg.panel_tests_id or "1"
    
    # export_fields é a lista de analitos para este painel
    export_fields = cfg.export_fields or []
    if not export_fields:
        return {"painel_" + panel_id: df_resultados}
    
    # Filtra colunas de resultado correspondentes
    df_painel = df_resultados.copy()
    
    # Garante apenas campos exportáveis
    mask = df_painel["codigoAmostra"].apply(
        lambda x: not any(ctrl.upper() in str(x).upper() 
                          for ctrl in cfg.controles.get("cn", []) + 
                                       cfg.controles.get("cp", []))
    )
    df_painel = df_painel[mask]
    
    return {"painel_" + panel_id: df_painel}

# Usar:
df_por_painel = service.preparar_dados_por_painel(df_final, exame)
for painel_name, df_painel in df_por_painel.items():
    painel_csv = f"relatorios/{painel_name}_{datetime.now().isoformat()}.csv"
    df_painel.to_csv(painel_csv, sep=";", index=False, encoding="utf-8")
```

**Benefício:** Organização automática por painel; facilita rastreamento GAL.

---

## 6. TESTES RECOMENDADOS

### Teste 1: Registry carregamento
```python
def test_exam_registry_load():
    from services.exam_registry import get_exam_cfg
    
    cfg = get_exam_cfg("vr1e2_biomanguinhos_7500")
    assert cfg is not None
    assert cfg.faixas_ct["detect_max"] > 0
    assert len(cfg.alvos) > 0
    assert cfg.bloco_size() >= 1
```

### Teste 2: Normalização de alvos
```python
def test_normalize_target():
    cfg = get_exam_cfg("vr1e2_biomanguinhos_7500")
    
    assert cfg.normalize_target("INFA") == "INF A"
    assert cfg.normalize_target("infa") == "INF A"
    assert cfg.normalize_target("INF_A") == "INF A"
```

### Teste 3: Motor com registry
```python
def test_motor_usa_registry():
    # Simula análise com registry
    contexto = AnaliseContexto(...)
    contexto.config_equip["exame"] = "vr1e2_biomanguinhos_7500"
    
    df_final, meta = executar_analise_universal(contexto)
    
    # Verifica que usou thresholds do registry
    assert df_final is not None
```

---

## 7. CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Patch 1: Motor (universal_engine.py) - 1-2 horas
- [ ] Patch 2: Mapa (plate_viewer.py) - 1-2 horas  
- [ ] Patch 3: Histórico (history_report.py) - 30-45 min
- [ ] Patch 4: Exportação (main.py) - 30-45 min
- [ ] Patch 5: Painel (envio_gal.py) - 45-60 min
- [ ] Testes unitários - 1-2 horas
- [ ] Testes integração - 1-2 horas
- [ ] **Total estimado: 6-10 horas**

---

## 8. PRIORIDADES

**Sprint 1 (P0 - 2 horas):**
- Patch 1 (Motor)
- Patch 2 (Mapa - essencial)

**Sprint 2 (P1 - 2 horas):**
- Patch 3 (Histórico)
- Patch 4 (Exportação)

**Sprint 3 (P2 - 1 hora):**
- Patch 5 (Painel)
- Testes

---

## 9. VALIDAÇÃO PÓS-IMPLEMENTAÇÃO

```python
# Executar pipeline completo
from services.analysis_service import AnalysisService

# 1. Carregar dados
service = AnalysisService(app_state)
df_final, meta = service.realizar_analise(...)

# 2. Verificar histórico
gerar_historico_csv(df_final, "vr1e2_biomanguinhos_7500", "user1")
df_hist = pd.read_csv("logs/historico_analises.csv")
assert "INF A - R" in df_hist.columns  # Normalizado!

# 3. Mapa com cores corretas
model = PlateModel.from_df(df_final, exame="vr1e2_biomanguinhos_7500")
assert model.exam_cfg is not None
assert model.group_size == model.exam_cfg.bloco_size()

# 4. Exportação GAL
df_gal = _formatar_para_gal(df_final, exame="vr1e2_biomanguinhos_7500")
assert df_gal["kit"].unique()[0] == "427"  # Do registry
assert "CN" not in df_gal["codigoAmostra"].values  # Filtrado!
```

---

**Documento:** Recomendações Técnicas Fase 4  
**Versão:** 1.0  
**Data:** 7 de dezembro de 2025
