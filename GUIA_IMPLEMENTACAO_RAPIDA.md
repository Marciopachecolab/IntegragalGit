# GUIA RÁPIDO - IMPLEMENTAÇÃO FASE 4
## 5 Patches essenciais em 30 minutos cada

---

## PATCH 1: Motor usa Registry Faixas CT (30 min)
**Arquivo:** `services/universal_engine.py` | **Linha:** ~263

### O que buscar:
```python
def _aplicar_regras_ct_e_interpretacao(
    df_norm: pd.DataFrame, contexto: AnaliseContexto
) -> pd.DataFrame:
    cfg = contexto.config_regras  # ← AQUI
```

### O que TROCAR:
```python
# ANTES (2 linhas):
cfg = contexto.config_regras
def as_float(key, default):

# DEPOIS (8 linhas):
from services.exam_registry import get_exam_cfg
exame_nome = contexto.config_equip.get("exame", "")
exam_cfg = get_exam_cfg(exame_nome)

if exam_cfg and exam_cfg.faixas_ct:
    cfg = exam_cfg.faixas_ct
else:
    cfg = contexto.config_regras  # fallback
```

### Checklist:
- [ ] Adicionar import `get_exam_cfg`
- [ ] Ler `exame_nome` de contexto
- [ ] Carregar `exam_cfg`
- [ ] Usar `exam_cfg.faixas_ct` se disponível
- [ ] Fallback para `config_regras`

---

## PATCH 2: Mapa Carrega exam_cfg (30 min)
**Arquivo:** `services/plate_viewer.py` | **Linha:** ~100

### O que buscar:
```python
@classmethod
def from_df(
    cls,
    df_final: pd.DataFrame,
    group_size: Optional[int] = None,
    exame: Optional[str] = None,
) -> "PlateModel":
    model = cls()
    # ... resto do código ...
```

### O que TROCAR (após `model = cls()`):
```python
# ADICIONAR após linha "model = cls()":
if exame:
    from services.exam_registry import get_exam_cfg
    model.exam_cfg = get_exam_cfg(exame)

# MODIFICAR group_size:
if group_size is None and model.exam_cfg:
    group_size = model.exam_cfg.bloco_size()
model.group_size = group_size or 1
```

### Checklist:
- [ ] Carregar exam_cfg se exame fornecido
- [ ] Usar bloco_size() se não group_size fornecido
- [ ] Atribuir a model.group_size

---

## PATCH 3: Histórico Normaliza Alvos (30 min)
**Arquivo:** `services/history_report.py` | **Linha:** ~133

### O que buscar:
```python
for col_res, col_ct in targets:
    base = str(col_res).replace("Resultado_", "").strip()
    res_val = r.get(col_res)
    res_code = _map_result(res_val)
    linha[f"{base} - R"] = f"{base} - {res_code}" if res_code else ""
```

### O que TROCAR:
```python
for col_res, col_ct in targets:
    base_raw = str(col_res).replace("Resultado_", "").strip()
    # ADICIONAR: usar normalize_target
    base = cfg.normalize_target(base_raw)
    
    res_val = r.get(col_res)
    res_code = _map_result(res_val)
    linha[f"{base} - R"] = f"{base} - {res_code}" if res_code else ""  # Usa 'base' normalizado
    
    if col_ct and col_ct in r:
        linha[f"{base} - CT"] = _fmt_ct(r.get(col_ct))  # Usa 'base' normalizado
```

### Checklist:
- [ ] Extrair base_raw (nome bruto)
- [ ] Normalizar: `base = cfg.normalize_target(base_raw)`
- [ ] Usar `base` (normalizado) em nomes de colunas
- [ ] Aplicar em ambas linhas "- R" e "- CT"

---

## PATCH 4: Exportação usa cfg.controles (30 min)
**Arquivo:** `main.py` | **Linha:** ~115

### O que buscar:
```python
def _exportavel(code: str) -> bool:
    if not code:
        return False
    c = code.upper()
    if "CN" in c or "CP" in c:  # ← AQUI
        return False
    return c.isdigit()
```

### O que TROCAR:
```python
def _exportavel(code: str, cfg) -> bool:  # Adicionar parâmetro cfg
    if not code:
        return False
    c = str(code).upper()
    
    # Usar cfg.controles se disponível
    if cfg and cfg.controles:
        cn_list = [str(x).upper() for x in cfg.controles.get("cn", [])]
        cp_list = [str(x).upper() for x in cfg.controles.get("cp", [])]
        if c in cn_list or c in cp_list:
            return False
    else:
        # Fallback hardcoded
        if "CN" in c or "CP" in c:
            return False
    
    return c.isdigit()

# USAR em export_mask:
export_mask = cod_col.apply(lambda x: _exportavel(x, cfg))  # Passar cfg
```

### Checklist:
- [ ] Adicionar parâmetro `cfg` na função
- [ ] Extrair CN/CP de cfg.controles se disponível
- [ ] Fallback para hardcoded se não disponível
- [ ] Passar `cfg` ao chamar apply()

---

## PATCH 5: Painel CSV (60 min)
**Arquivo:** `exportacao/envio_gal.py` | **Localização:** novo método

### O que ADICIONAR (novo método em GalService):
```python
def preparar_dados_por_painel(
    self, 
    df_resultados: pd.DataFrame, 
    exame: str
) -> Dict[str, pd.DataFrame]:
    """Organiza dados por painel conforme export_fields."""
    from services.exam_registry import get_exam_cfg
    
    cfg = get_exam_cfg(exame)
    panel_id = cfg.panel_tests_id or "1"
    
    # Filtra colunas exportáveis (não CN/CP)
    mask = df_resultados["codigoAmostra"].apply(
        lambda x: str(x).upper().isdigit()
    )
    df_painel = df_resultados[mask].copy()
    
    return {"painel_" + panel_id: df_painel}
```

### Como USAR:
```python
# Em abrir_janela_envio_gal():
df_por_painel = service.preparar_dados_por_painel(df_final, exame)

for painel_name, df_painel in df_por_painel.items():
    timestamp = datetime.now().isoformat().replace(":", "")
    filename = f"relatorios/{painel_name}_{timestamp}.csv"
    df_painel.to_csv(filename, sep=";", index=False, encoding="utf-8")
```

### Checklist:
- [ ] Criar método novo preparar_dados_por_painel()
- [ ] Buscar panel_tests_id do registry
- [ ] Filtrar apenas numéricos (não CN/CP)
- [ ] Retornar Dict com painel name como chave
- [ ] Chamar método ao salvar resultados

---

## ORDEM DE EXECUÇÃO (90 min total)

```
⏱️ 0:00 - Iniciar
├─ 0:30 [PATCH 1] Motor faixas_ct ✓
├─ 1:00 [PATCH 2] Mapa exam_cfg ✓
├─ 1:30 [PATCH 3] Histórico normalize ✓
├─ 2:00 [PATCH 4] Exportação cfg.controles ✓
├─ 3:00 [PATCH 5] Painel CSV ✓
└─ 3:30 ✓ PRONTO

Testes rápidos: 30 min extra (opcional)
```

---

## TESTES RÁPIDOS (Validação)

### Teste 1: Motor (5 min)
```python
# rodar no terminal:
python -c "
from services.universal_engine import AnaliseContexto, executar_analise_universal
# Verificar que cfg.faixas_ct é usado (check log ou breakpoint)
print('✓ Motor OK' if True else '✗ Falha')
"
```

### Teste 2: Mapa (5 min)
```python
# rodar:
python -c "
from services.plate_viewer import PlateModel
import pandas as pd
df = pd.DataFrame({'Poco': ['A01', 'A02'], 'Resultado_SC2': [1, 2]})
model = PlateModel.from_df(df, exame='vr1e2_biomanguinhos_7500')
print('✓ Mapa carregou exam_cfg' if model.exam_cfg else '✗ Falha')
"
```

### Teste 3: Histórico (5 min)
```python
# rodar:
python -c "
from services.history_report import gerar_historico_csv
import pandas as pd
df = pd.DataFrame({'Poco': ['A01'], 'Codigo': ['123'], 'Amostra': ['S1'], 'Status_Corrida': ['OK']})
gerar_historico_csv(df, 'vr1e2_biomanguinhos_7500', 'user1')
# Verificar que histórico tem colunas normalizadas
print('✓ Histórico OK')
"
```

### Teste 4: Exportação (5 min)
```python
# rodar:
python -c "
from main import _formatar_para_gal
from services.exam_registry import get_exam_cfg
import pandas as pd
cfg = get_exam_cfg('vr1e2_biomanguinhos_7500')
df = pd.DataFrame({'Codigo': ['123', 'CN'], 'Resultado_SC2': [1, 0]})
df_gal = _formatar_para_gal(df, exam_cfg=cfg)
print('✓ Exportação OK' if 'CN' not in df_gal['codigoAmostra'].values else '✗ CN não filtrado')
"
```

---

## VERIFICAÇÃO VISUAL

Após patches, verificar no código:

### Motor
```python
✓ exam_cfg = get_exam_cfg(exame_nome)
✓ cfg.faixas_ct["detect_max"] usado
✓ fallback se cfg vazio
```

### Mapa
```python
✓ model.exam_cfg carregado
✓ bloco_size() chamado
✓ group_size atribuído
```

### Histórico
```python
✓ base_norm = cfg.normalize_target(base_raw)
✓ Colunas usam base_norm (não base_raw)
```

### Exportação
```python
✓ _exportavel() recebe cfg
✓ cfg.controles iterado
✓ fallback CN/CP presente
```

### Painel
```python
✓ preparar_dados_por_painel() existe
✓ Filtra não CN/CP
✓ Retorna Dict com painel_X
```

---

## ROLLBACK RÁPIDO

Se algum patch quebrar:

```bash
# Ver último commit:
git log --oneline | head -5

# Reverter um arquivo:
git checkout HEAD -- services/universal_engine.py

# Reverter tudo:
git reset --hard HEAD~1
```

---

## DÚVIDAS FREQUENTES

**P: E se cfg.faixas_ct vier vazio?**
R: Usa fallback `contexto.config_regras` (compatibilidade garantida).

**P: Como saber se normalize_target() funcionou?**
R: Verifique no histórico CSV se coluna é "INF A" (normalizado) ou "INFA" (não).

**P: O painel CSV é obrigatório?**
R: Não, é P2. Se tempo limitado, fazer P1 primeiro.

**P: Posso fazer patches em ordem diferente?**
R: Sim! P0 antes (Motor + Mapa), depois P1 (Histórico + Exportação).

---

## REFERÊNCIA RÁPIDA

```
Arquivo            | Linha | O quê                | Patch #
=====================================
universal_engine.py | 263  | Faixas CT           | 1
plate_viewer.py     | 100  | exam_cfg load       | 2
history_report.py   | 133  | normalize_target    | 3
main.py             | 115  | _exportavel cfg     | 4
envio_gal.py        | novo | preparar_dados      | 5
```

---

**Tempo estimado:** 90 minutos (+ 30 min testes opcionais)  
**Complexidade:** Baixa a Média  
**Risco:** Baixo (todos com fallback ou compatibilidade)  
**Gerado:** 7 de dezembro de 2025
