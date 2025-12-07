# RELATÃ“RIO DE ANÃ�LISE - FASE 4: INTEGRAÃ‡ÃƒO DO REGISTRY
**Data:** 7 de dezembro de 2025  
**Sistema:** IntegragalGit (c:\Users\marci\downloads\integragal)  
**Status:** Parcialmente implementado

---

## 1. RESUMO EXECUTIVO

A Fase 4 busca consolidar a integraÃ§Ã£o do **ExamRegistry** em 4 componentes principais:
- **Engine** (universal_engine.py)
- **HistÃ³rico** (history_report.py)
- **Mapa** (plate_viewer.py)
- **ExportaÃ§Ã£o GAL** (menu_handler/main)

### Status Geral: ğŸŸ¡ 60-70% IMPLEMENTADO

---

## 2. ANÃ�LISE POR COMPONENTE

### 2.1 ENGINE (universal_engine.py) - ğŸŸ¢ BEM INTEGRADO

#### âœ… Implementado:
1. **Leitura e normalizaÃ§Ã£o** (linhas 220-240):
   - `_ler_e_normalizar_arquivo()` lÃª arquivo CSV/XLSX
   - Normaliza colunas: poco, amostra, alvo, ct
   - Valida presenÃ§a de colunas obrigatÃ³rias

2. **IntegraÃ§Ã£o com gabarito** (linhas 243-260):
   - `_integrar_com_gabarito_extracao()` merge dados com gabarito de extraÃ§Ã£o
   - Preserva sample_name do gabarito quando disponÃ­vel

3. **Regras CT e interpretaÃ§Ã£o** (linhas 263+):
   - `_aplicar_regras_ct_e_interpretacao()` aplica thresholds
   - Usa `config_regras` com CT_DETECTAVEL_MAX, CT_INCONCLUSIVO_MIN/MAX, CT_RP_MIN/MAX

#### âš ï¸� LACUNAS:
- **Registry NÃƒO Ã© usado** nas regras CT
  - Linhas 263-300: LÃª valores de `contexto.config_regras` (legado CSV)
  - **DEVERIA:** `cfg = get_exam_cfg(exame); ct_detect_max = cfg.faixas_ct["detect_max"]`
  
- **normalize_target() NÃƒO Ã© usado**
  - Alvos nÃ£o sÃ£o normalizados via `cfg.normalize_target()`
  - Resultados e CTs nÃ£o consolidam variaÃ§Ãµes (ex: INF A / INFA / Inf_a)

- **Blocos e esquema_agrupamento NÃƒO implementado**
  - `_determine_status_corrida()` nÃ£o usa `cfg.bloco_size()`
  - Agrupamento de poÃ§os (blocos) nÃ£o respeita esquema_agrupamento

#### ğŸ”´ RecomendaÃ§Ã£o:
```python
# LINHA ~263: substituir
cfg = get_exam_cfg(exame)  # â†� ADICIONAR
ct_detect_max = cfg.faixas_ct["detect_max"]  # â†� USE REGISTRY
ct_inconc_min = cfg.faixas_ct["inconc_min"]
ct_inconc_max = cfg.faixas_ct["inconc_max"]
ct_rp_min = cfg.faixas_ct["rp_min"]
ct_rp_max = cfg.faixas_ct["rp_max"]
```

---

### 2.2 HISTÃ“RICO (history_report.py) - ğŸŸ¡ PARCIALMENTE INTEGRADO

#### âœ… Implementado:
1. **Uso do Registry** (linha 7):
   - `from services.exam_registry import get_exam_cfg`
   - `cfg = get_exam_cfg(exame)` âœ“

2. **FunÃ§Ã£o `_norm()`** (linhas 101-102):
   - Normaliza nomes de colunas para busca case-insensitive

3. **Estrutura de targets** (linhas 123-150):
   - Monta lista `targets` com pares (col_res, col_ct)
   - Inclui alvos do registry via `cfg.alvos`

4. **GeraÃ§Ã£o de linhas** (linhas 151+):
   - Loop sobre `df_final.iterrows()`
   - Separa CN/CP/nÃ£o numÃ©ricos: `status_gal = "tipo nao enviavel"`
   - Formata CT com 3 casas decimais: `_fmt_ct()` âœ“

#### âš ï¸� LACUNAS:
1. **Mapa de alvos NÃƒO Ã© usado**
   - Linha 133: `base = str(col_res).replace("Resultado_", "").strip()`
   - **DEVERIA:** `base = cfg.normalize_target(alvo)` para nomes normalizados
   - Coluna de histÃ³rico fica com nome nÃ£o normalizado

2. **mapa_alvos nÃ£o aplicado**
   - Ex: `cfg.mapa_alvos = {"INFA": "INF A"}` existe mas NÃƒO Ã© usado
   - Linhas do histÃ³rico nÃ£o usam nomes canonicalizados

3. **Colunas de saÃ­da incompletas**
   - NÃ£o segue padrÃ£o "ALVO - R / ALVO - CT para TODOS alvos+RPs"
   - RP CTs aparecem mas sem nomenclatura consistente

#### ğŸ”´ RecomendaÃ§Ã£o:
```python
# LINHA ~133: usar normalization
for alvo in cfg.alvos:
    alvo_norm = cfg.normalize_target(alvo)  # â†� ADICIONAR
    alvo_no_space = alvo_norm.replace(" ", "")
    col_res = f"Resultado_{alvo_no_space}"
    # ...
    linha[f"{alvo_norm} - R"] = f"{alvo_norm} - {res_code}"  # â†� USE ALVO_NORM
    linha[f"{alvo_norm} - CT"] = _fmt_ct(...)
```

---

### 2.3 MAPA / PLATE_VIEWER (plate_viewer.py) - ğŸŸ¡ PARCIALMENTE INTEGRADO

#### âœ… Implementado:
1. **Estrutura bÃ¡sica** (linhas 1-60):
   - `PlateModel` com `exam_cfg` opcional
   - `from_df()` classmethod para construÃ§Ã£o
   - `WellData` dataclass com targets

2. **Cores por status** (linhas 30-40):
   - STATUS_COLORS com POSITIVE/NEGATIVE/INCONCLUSIVE/CONTROL_CN/CONTROL_CP
   - **MAS:** cores NÃƒO sÃ£o parametrizÃ¡veis por `cfg.faixas_ct`

#### âš ï¸� LACUNAS:
1. **Registry NÃƒO carregado em from_df()**
   - Linha 100: `exame: Optional[str] = None` recebido mas NÃƒO usado
   - `self.exam_cfg` nunca Ã© preenchido com `get_exam_cfg(exame)`

2. **Faixas CT (RP) NÃƒO respeitadas**
   - Cores de RP deveriam ser baseadas em `cfg.faixas_ct["rp_min"]/["rp_max"]`
   - Linhas 250+: RP sÃ£o codificadas como azul fixo
   - **DEVERIA:** avaliar se CT estÃ¡ em faixa, colorir verde/amarelo/vermelho

3. **Blocos NÃƒO agrupam conforme cfg.bloco_size()**
   - `self.group_size` pode ser definido (linha ~80)
   - **MAS:** `cfg.bloco_size()` nunca Ã© chamado
   - Esquema_agrupamento Ã© ignorado

4. **Alvos NÃƒO normalizados**
   - Linha 240: `for alvo in targets:` usa raw targets
   - Cores/contornos nÃ£o consideram `cfg.normalize_target()`

5. **Controles azuis nÃ£o verificam cfg.controles**
   - Linha 220: `is_control = (code in ["CN", "CP"])`  hardcoded
   - **DEVERIA:** `is_control = (code in cfg.controles.get("cn", []) or code in cfg.controles.get("cp", []))`

#### ğŸ”´ RecomendaÃ§Ã£o:
```python
# LINHA ~100: adicionar carregamento
@classmethod
def from_df(cls, df_final, group_size=None, exame=None):
    model = cls()
    if exame:
        model.exam_cfg = get_exam_cfg(exame)  # â†� ADICIONAR
    
    # Usar group_size do registry se nÃ£o fornecido
    if group_size is None and model.exam_cfg:
        group_size = model.exam_cfg.bloco_size()  # â†� ADICIONAR
    model.group_size = group_size or 1
    
    # ... resto do cÃ³digo
```

---

### 2.4 EXPORTAÃ‡ÃƒO GAL (envio_gal.py / main.py) - ğŸŸ¡ PARCIALMENTE INTEGRADO

#### âœ… Implementado em main.py:
1. **_formatar_para_gal()** (linhas 1-70):
   - Recebe `exam_cfg` ou busca via `get_exam_cfg(exame)`
   - Usa `cfg.kit_codigo`, `cfg.panel_tests_id`, `cfg.nome_exame`
   - Normaliza alvos via `cfg.normalize_target()`

2. **Filtro de exportÃ¡veis** (linhas 115-120):
   - `_exportavel()` valida cÃ³digo: nÃ£o CN/CP, apenas numÃ©ricos
   - **MAS:** implementaÃ§Ã£o manual, poderia usar `cfg.controles`

3. **export_fields** (linhas 123-130):
   - Usa `cfg.export_fields` quando disponÃ­vel
   - Fallback para lista padrÃ£o (INF A, INF B, ADV, etc.)

#### âš ï¸� LACUNAS:
1. **Mapeamento 1/2/3/"" NÃƒO finalizado**
   - Linha ~165: resultado vazio (nÃ£o mapeado)
   - **DEVERIA:** resultado="1"/"2"/"3"/"" conforme `_map_result()`

2. **CN/CP NÃƒO filtram dinamicamente**
   - Usa hardcoded `"CN" in c or "CP" in c`
   - **DEVERIA:** usar `cfg.controles["cn"]` e `cfg.controles["cp"]`

3. **GeraÃ§Ã£o CSV do painel correspondente**
   - envio_gal.py NÃƒO cria arquivo por painel automaticamente
   - Deveria: se `cfg.panel_tests_id = "1"`, criar painel_1.csv com export_fields[1]

4. **panel_tests_id nÃ£o robusto**
   - Linha ~130 (main.py): `df_out["painel"] = cfg.panel_tests_id or "1"`
   - **MAS:** se cfg vem de fallback, panel_tests_id fica vazio

#### ğŸ”´ RecomendaÃ§Ã£o:
```python
# main.py LINHA ~160: adicionar mapeamento completo
def _map_result(val):
    # ... cÃ³digo existente ...
    if "detect" in s and "nao" not in s:
        return "1"
    if ("nao" in s or "nÃ£o" in s) and "detect" in s:
        return "2"
    if "inconcl" in s:
        return "3"
    return ""  # â†� inconclusivo ou invÃ¡lido vira vazio

# envio_gal.py: usar cfg.controles
def _is_controle(code, cfg):
    c = str(code).upper()
    return c in [str(x).upper() for x in cfg.controles.get("cn", [])] or \
           c in [str(x).upper() for x in cfg.controles.get("cp", [])]
```

---

## 3. VALIDAÃ‡Ã•ES TÃ‰CNICAS

### 3.1 Registry Carregamento âœ“
```python
# exam_registry.py estÃ¡ operacional
cfg = get_exam_cfg("vr1e2_biomanguinhos_7500")
# Retorna ExamConfig com alvos, faixas_ct, normalize_target(), bloco_size()
```

### 3.2 ExamConfig Fields âœ“
```python
@dataclass
class ExamConfig:
    nome_exame: str
    alvos: List[str]           # â†� Motor/HistÃ³rico/Mapa DEVEM usar
    mapa_alvos: Dict[str, str] # â†� Normalization chave!
    faixas_ct: Dict[str, float]# â†� CT thresholds (Motor/Mapa DEVEM usar)
    rps: List[str]             # â†� HistÃ³rico/Mapa DEVEM iterar
    export_fields: List[str]   # â†� ExportaÃ§Ã£o DEVE usar
    panel_tests_id: str        # â†� GAL panel mapping
    controles: Dict[str, List] # â†� CN/CP dinÃ¢micos
    kit_codigo: Any            # â†� GAL kit field
    bloco_size(): int          # â†� Mapa DEVE chamar
    normalize_target(name): str# â†� Todos DEVEM usar
```

### 3.3 JSON Config Samples
```
config/exams/vr1e2_biomanguinhos_7500.json
{
  "nome_exame": "VR1E2 - Biomanguinhos 7500",
  "alvos": ["SC2", "INF A", "INF B", "ADV", "HMPV", "RSV", "HRV", "RP"],
  "mapa_alvos": {
    "INFA": "INF A",
    "INFB": "INF B",
    "ADV": "ADV",
    "SC2": "SARS-COV-2"
  },
  "faixas_ct": {
    "detect_max": 37.0,
    "inconc_min": 37.01,
    "inconc_max": 40.0,
    "rp_min": 15.0,
    "rp_max": 35.0
  },
  "rps": ["RP"],
  "export_fields": ["influenzaa", "influenzab", "adenovirus", ...],
  "panel_tests_id": "1",
  "kit_codigo": "427",
  "esquema_agrupamento": "96->96"
}
```

---

## 4. ROADMAP RECOMENDADO (PRIORIDADE)

### ğŸ”´ CRÃ�TICO (P0) - Afeta anÃ¡lise:
1. **Motor (universal_engine.py)**
   - [ ] Substituir `config_regras` por `cfg.faixas_ct` 
   - [ ] Normalizar alvos via `cfg.normalize_target()`
   - [ ] Implementar blocos via `cfg.bloco_size()`

2. **Mapa (plate_viewer.py)**
   - [ ] Carregar `exam_cfg` em `from_df()`
   - [ ] Colorir RP conforme `cfg.faixas_ct`
   - [ ] Usar `cfg.bloco_size()` para agrupamento

### ğŸŸ  ALTO (P1) - Afeta histÃ³rico/exportaÃ§Ã£o:
3. **HistÃ³rico (history_report.py)**
   - [ ] Usar `cfg.normalize_target()` em nomes de colunas
   - [ ] Aplicar `cfg.mapa_alvos` em outputs

4. **ExportaÃ§Ã£o GAL (main.py/envio_gal.py)**
   - [ ] Usar `cfg.controles` dinamicamente
   - [ ] Completar mapeamento 1/2/3 em _map_result()
   - [ ] Gerar CSV por painel

### ğŸŸ¡ MÃ‰DIO (P2) - Robustez:
5. **Testes**
   - [ ] Unit tests para normalize_target()
   - [ ] Integration tests para fluxo motorâ†’histÃ³ricoâ†’mapaâ†’exportaÃ§Ã£o
   - [ ] ValidaÃ§Ã£o de JSON configs

---

## 5. IMPACTO E BENEFÃ�CIOS

### ApÃ³s ImplementaÃ§Ã£o Completa:
âœ… **Alvos normalizados** em todo pipeline (AC/AC nÃ£o quebra)  
âœ… **CT thresholds dinÃ¢micos** por exame (nÃ£o hardcoded)  
âœ… **Controles robustos** (CN/CP/custom via config)  
âœ… **Blocos de placa** respeitam esquema_agrupamento  
âœ… **ExportaÃ§Ã£o GAL** usa registry (um ponto de configuraÃ§Ã£o)  
âœ… **HistÃ³rico consistente** com nomenclatura normalizada  

---

## 6. ARQUIVOS ENVOLVIDOS

```
USAR REGISTRY:
â”œâ”€â”€ services/
â”‚   â”œâ”€â”€ universal_engine.py      (P0 - CrÃ­tico)
â”‚   â”œâ”€â”€ history_report.py        (P1 - Alto)
â”‚   â”œâ”€â”€ plate_viewer.py          (P0 - CrÃ­tico)
â”‚   â””â”€â”€ exam_registry.py         (Base - OK âœ“)
â”œâ”€â”€ exportacao/
â”‚   â””â”€â”€ envio_gal.py             (P1 - Alto)
â”œâ”€â”€ main.py                      (P1 - Alto)
â””â”€â”€ config/
    â””â”€â”€ exams/
        â””â”€â”€ *.json               (Configs - OK âœ“)
```

---

## 7. CONCLUSÃƒO

**Fase 4 estÃ¡ ~60% implementado**:
- âœ… Registry estrutura e carregamento OK
- âœ… HistÃ³rico usa cfg bÃ¡sico
- âœ… Main.py formata_para_gal OK
- âš ï¸� Motor nÃ£o usa faixas_ct do registry
- âš ï¸� Mapa nÃ£o carrega exam_cfg
- âš ï¸� NormalizaÃ§Ã£o de alvos incompleta

**PrÃ³ximos passos:**
1. Refatorar universal_engine.py para usar faixas_ct
2. Carregar exam_cfg em plate_viewer.from_df()
3. Aplicar normalize_target() sistemicamente
4. Completar exportaÃ§Ã£o com panel_tests_id

---

**Gerado em:** 7 de dezembro de 2025  
**Status atual:** AnÃ¡lise concluÃ­da âœ“
