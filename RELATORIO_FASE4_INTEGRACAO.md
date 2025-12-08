# RELATÃ“RIO DE ANÃ�LISE - FASE 4: INTEGRAÃ‡ÃƒO DO REGISTRY

**Data:** 7 de dezembro de 2025  

**Sistema:** IntegragalGit (c:\Users\marci\downloads\integragal)  

**Status:** Parcialmente implementado



---



## 1. RESUMO EXECUTIVO



A Fase 4 busca consolidar a integração do **ExamRegistry** em 4 componentes principais:

- **Engine** (universal_engine.py)

- **Histórico** (history_report.py)

- **Mapa** (plate_viewer.py)

- **Exportação GAL** (menu_handler/main)



### Status Geral: ğŸŸ¡ 60-70% IMPLEMENTADO



---



## 2. ANÃ�LISE POR COMPONENTE



### 2.1 ENGINE (universal_engine.py) - ğŸŸ¢ BEM INTEGRADO



#### âœ… Implementado:

1. **Leitura e normalização** (linhas 220-240):

   - `_ler_e_normalizar_arquivo()` lê arquivo CSV/XLSX

   - Normaliza colunas: poco, amostra, alvo, ct

   - Valida presença de colunas obrigatórias



2. **Integração com gabarito** (linhas 243-260):

   - `_integrar_com_gabarito_extracao()` merge dados com gabarito de extração

   - Preserva sample_name do gabarito quando disponível



3. **Regras CT e interpretação** (linhas 263+):

   - `_aplicar_regras_ct_e_interpretacao()` aplica thresholds

   - Usa `config_regras` com CT_DETECTAVEL_MAX, CT_INCONCLUSIVO_MIN/MAX, CT_RP_MIN/MAX



#### âš ï¸� LACUNAS:

- **Registry NÃƒO é usado** nas regras CT

  - Linhas 263-300: Lê valores de `contexto.config_regras` (legado CSV)

  - **DEVERIA:** `cfg = get_exam_cfg(exame); ct_detect_max = cfg.faixas_ct["detect_max"]`

  

- **normalize_target() NÃƒO é usado**

  - Alvos não são normalizados via `cfg.normalize_target()`

  - Resultados e CTs não consolidam variações (ex: INF A / INFA / Inf_a)



- **Blocos e esquema_agrupamento NÃƒO implementado**

  - `_determine_status_corrida()` não usa `cfg.bloco_size()`

  - Agrupamento de poços (blocos) não respeita esquema_agrupamento



#### ğŸ”´ Recomendação:

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



2. **Função `_norm()`** (linhas 101-102):

   - Normaliza nomes de colunas para busca case-insensitive



3. **Estrutura de targets** (linhas 123-150):

   - Monta lista `targets` com pares (col_res, col_ct)

   - Inclui alvos do registry via `cfg.alvos`



4. **Geração de linhas** (linhas 151+):

   - Loop sobre `df_final.iterrows()`

   - Separa CN/CP/não numéricos: `status_gal = "tipo nao enviavel"`

   - Formata CT com 3 casas decimais: `_fmt_ct()` âœ“



#### âš ï¸� LACUNAS:

1. **Mapa de alvos NÃƒO é usado**

   - Linha 133: `base = str(col_res).replace("Resultado_", "").strip()`

   - **DEVERIA:** `base = cfg.normalize_target(alvo)` para nomes normalizados

   - Coluna de histórico fica com nome não normalizado



2. **mapa_alvos não aplicado**

   - Ex: `cfg.mapa_alvos = {"INFA": "INF A"}` existe mas NÃƒO é usado

   - Linhas do histórico não usam nomes canonicalizados



3. **Colunas de saída incompletas**

   - Não segue padrão "ALVO - R / ALVO - CT para TODOS alvos+RPs"

   - RP CTs aparecem mas sem nomenclatura consistente



#### ğŸ”´ Recomendação:

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

1. **Estrutura básica** (linhas 1-60):

   - `PlateModel` com `exam_cfg` opcional

   - `from_df()` classmethod para construção

   - `WellData` dataclass com targets



2. **Cores por status** (linhas 30-40):

   - STATUS_COLORS com POSITIVE/NEGATIVE/INCONCLUSIVE/CONTROL_CN/CONTROL_CP

   - **MAS:** cores NÃƒO são parametrizáveis por `cfg.faixas_ct`



#### âš ï¸� LACUNAS:

1. **Registry NÃƒO carregado em from_df()**

   - Linha 100: `exame: Optional[str] = None` recebido mas NÃƒO usado

   - `self.exam_cfg` nunca é preenchido com `get_exam_cfg(exame)`



2. **Faixas CT (RP) NÃƒO respeitadas**

   - Cores de RP deveriam ser baseadas em `cfg.faixas_ct["rp_min"]/["rp_max"]`

   - Linhas 250+: RP são codificadas como azul fixo

   - **DEVERIA:** avaliar se CT está em faixa, colorir verde/amarelo/vermelho



3. **Blocos NÃƒO agrupam conforme cfg.bloco_size()**

   - `self.group_size` pode ser definido (linha ~80)

   - **MAS:** `cfg.bloco_size()` nunca é chamado

   - Esquema_agrupamento é ignorado



4. **Alvos NÃƒO normalizados**

   - Linha 240: `for alvo in targets:` usa raw targets

   - Cores/contornos não consideram `cfg.normalize_target()`



5. **Controles azuis não verificam cfg.controles**

   - Linha 220: `is_control = (code in ["CN", "CP"])`  hardcoded

   - **DEVERIA:** `is_control = (code in cfg.controles.get("cn", []) or code in cfg.controles.get("cp", []))`



#### ğŸ”´ Recomendação:

```python

# LINHA ~100: adicionar carregamento

@classmethod

def from_df(cls, df_final, group_size=None, exame=None):

    model = cls()

    if exame:

        model.exam_cfg = get_exam_cfg(exame)  # â†� ADICIONAR

    

    # Usar group_size do registry se não fornecido

    if group_size is None and model.exam_cfg:

        group_size = model.exam_cfg.bloco_size()  # â†� ADICIONAR

    model.group_size = group_size or 1

    

    # ... resto do código

```



---



### 2.4 EXPORTAÃ‡ÃƒO GAL (envio_gal.py / main.py) - ğŸŸ¡ PARCIALMENTE INTEGRADO



#### âœ… Implementado em main.py:

1. **_formatar_para_gal()** (linhas 1-70):

   - Recebe `exam_cfg` ou busca via `get_exam_cfg(exame)`

   - Usa `cfg.kit_codigo`, `cfg.panel_tests_id`, `cfg.nome_exame`

   - Normaliza alvos via `cfg.normalize_target()`



2. **Filtro de exportáveis** (linhas 115-120):

   - `_exportavel()` valida código: não CN/CP, apenas numéricos

   - **MAS:** implementação manual, poderia usar `cfg.controles`



3. **export_fields** (linhas 123-130):

   - Usa `cfg.export_fields` quando disponível

   - Fallback para lista padrão (INF A, INF B, ADV, etc.)



#### âš ï¸� LACUNAS:

1. **Mapeamento 1/2/3/"" NÃƒO finalizado**

   - Linha ~165: resultado vazio (não mapeado)

   - **DEVERIA:** resultado="1"/"2"/"3"/"" conforme `_map_result()`



2. **CN/CP NÃƒO filtram dinamicamente**

   - Usa hardcoded `"CN" in c or "CP" in c`

   - **DEVERIA:** usar `cfg.controles["cn"]` e `cfg.controles["cp"]`



3. **Geração CSV do painel correspondente**

   - envio_gal.py NÃƒO cria arquivo por painel automaticamente

   - Deveria: se `cfg.panel_tests_id = "1"`, criar painel_1.csv com export_fields[1]



4. **panel_tests_id não robusto**

   - Linha ~130 (main.py): `df_out["painel"] = cfg.panel_tests_id or "1"`

   - **MAS:** se cfg vem de fallback, panel_tests_id fica vazio



#### ğŸ”´ Recomendação:

```python

# main.py LINHA ~160: adicionar mapeamento completo

def _map_result(val):

    # ... código existente ...

    if "detect" in s and "nao" not in s:

        return "1"

    if ("nao" in s or "não" in s) and "detect" in s:

        return "2"

    if "inconcl" in s:

        return "3"

    return ""  # â†� inconclusivo ou inválido vira vazio



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

# exam_registry.py está operacional

cfg = get_exam_cfg("vr1e2_biomanguinhos_7500")

# Retorna ExamConfig com alvos, faixas_ct, normalize_target(), bloco_size()

```



### 3.2 ExamConfig Fields âœ“

```python

@dataclass

class ExamConfig:

    nome_exame: str

    alvos: List[str]           # â†� Motor/Histórico/Mapa DEVEM usar

    mapa_alvos: Dict[str, str] # â†� Normalization chave!

    faixas_ct: Dict[str, float]# â†� CT thresholds (Motor/Mapa DEVEM usar)

    rps: List[str]             # â†� Histórico/Mapa DEVEM iterar

    export_fields: List[str]   # â†� Exportação DEVE usar

    panel_tests_id: str        # â†� GAL panel mapping

    controles: Dict[str, List] # â†� CN/CP dinâmicos

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



### ğŸ”´ CRÃ�TICO (P0) - Afeta análise:

1. **Motor (universal_engine.py)**

   - [ ] Substituir `config_regras` por `cfg.faixas_ct` 

   - [ ] Normalizar alvos via `cfg.normalize_target()`

   - [ ] Implementar blocos via `cfg.bloco_size()`



2. **Mapa (plate_viewer.py)**

   - [ ] Carregar `exam_cfg` em `from_df()`

   - [ ] Colorir RP conforme `cfg.faixas_ct`

   - [ ] Usar `cfg.bloco_size()` para agrupamento



### ğŸŸ  ALTO (P1) - Afeta histórico/exportação:

3. **Histórico (history_report.py)**

   - [ ] Usar `cfg.normalize_target()` em nomes de colunas

   - [ ] Aplicar `cfg.mapa_alvos` em outputs



4. **Exportação GAL (main.py/envio_gal.py)**

   - [ ] Usar `cfg.controles` dinamicamente

   - [ ] Completar mapeamento 1/2/3 em _map_result()

   - [ ] Gerar CSV por painel



### ğŸŸ¡ MÃ‰DIO (P2) - Robustez:

5. **Testes**

   - [ ] Unit tests para normalize_target()

   - [ ] Integration tests para fluxo motorâ†’históricoâ†’mapaâ†’exportação

   - [ ] Validação de JSON configs



---



## 5. IMPACTO E BENEFÃ�CIOS



### Após Implementação Completa:

âœ… **Alvos normalizados** em todo pipeline (AC/AC não quebra)  

âœ… **CT thresholds dinâmicos** por exame (não hardcoded)  

âœ… **Controles robustos** (CN/CP/custom via config)  

âœ… **Blocos de placa** respeitam esquema_agrupamento  

âœ… **Exportação GAL** usa registry (um ponto de configuração)  

âœ… **Histórico consistente** com nomenclatura normalizada  



---



## 6. ARQUIVOS ENVOLVIDOS



```

USAR REGISTRY:

â”œâ”€â”€ services/

â”‚   â”œâ”€â”€ universal_engine.py      (P0 - Crítico)

â”‚   â”œâ”€â”€ history_report.py        (P1 - Alto)

â”‚   â”œâ”€â”€ plate_viewer.py          (P0 - Crítico)

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



**Fase 4 está ~60% implementado**:

- âœ… Registry estrutura e carregamento OK

- âœ… Histórico usa cfg básico

- âœ… Main.py formata_para_gal OK

- âš ï¸� Motor não usa faixas_ct do registry

- âš ï¸� Mapa não carrega exam_cfg

- âš ï¸� Normalização de alvos incompleta



**Próximos passos:**

1. Refatorar universal_engine.py para usar faixas_ct

2. Carregar exam_cfg em plate_viewer.from_df()

3. Aplicar normalize_target() sistemicamente

4. Completar exportação com panel_tests_id



---



**Gerado em:** 7 de dezembro de 2025  

**Status atual:** Análise concluída âœ“

