# üéì ETAPA 1 ‚Äî PREPARA√á√ÉO & DESIGN
**Status:** ‚öôÔ∏è IN PROGRESS  
**Tempo:** 1-2 horas  
**Data:** 2025-12-07  

---

## üìö LEITURA OBRIGAT√ìRIA (15 min)

### ‚úÖ J√° completada:

Voc√™ j√° leu:
- ‚úÖ RELATORIO_FASE5_ANALISE.md (se√ß√µes 1-4)
- ‚úÖ PLANO_FASE5_RESUMO.md (vis√£o geral)
- ‚úÖ PLANO_FASE5_ETAPAS.md (detalhes t√©cnicos)

### ‚è≠Ô∏è Revisar agora:

**Arquivo 1: ExamConfig Dataclass** (5 min)
- Local: `services/exam_registry.py:55-90`
- **15 campos que voc√™ precisa desenhar UI para:**

```python
@dataclass
class ExamConfig:
    nome_exame: str              # ‚Üê Campo de texto simples
    slug: str                    # ‚Üê Auto-gerado (nome_exame.lower().replace...)
    equipamento: str             # ‚Üê Dropdown (lista fixa?)
    tipo_placa_analitica: str    # ‚Üê Ex: "48", "96"
    esquema_agrupamento: str     # ‚Üê Ex: "96->48"
    kit_codigo: Any              # ‚Üê C√≥digo num√©rico
    alvos: List[str]             # ‚Üê Lista multi-linha (Text widget)
    mapa_alvos: Dict[str,str]    # ‚Üê Mapping JSON (Text widget)
    faixas_ct: Dict[str,float]   # ‚Üê JSON com 5 keys
    rps: List[str]               # ‚Üê Lista simples (Text widget)
    export_fields: List[str]     # ‚Üê Lista de campos export (Text)
    panel_tests_id: str          # ‚Üê ID num√©rico
    controles: Dict[str,List]    # ‚Üê CN/CP (controles negativos/positivos)
    comentarios: str             # ‚Üê Texto livre
    versao_protocolo: str        # ‚Üê Vers√£o (ex: "1.0")
```

**Arquivo 2: Exemplo Real (JSON)** (5 min)
- Local: `config/exams/vr1e2_biomanguinhos_7500.json`
- **Esse √© o LAYOUT exato que seu formul√°rio vai capturar:**

```json
{
  "nome_exame": "VR1e2 Biomanguinhos 7500",           ‚Üê ABA 1: B√°sico
  "slug": "vr1e2_biomanguinhos_7500",                  ‚Üì
  "equipamento": "7500 Real-Time",
  "tipo_placa_analitica": "48",
  "esquema_agrupamento": "96->48",
  "kit_codigo": 1140,
  
  "alvos": ["SC2", "HMPV", "INF A", ...],             ‚Üê ABA 2: Alvos
  "mapa_alvos": {"SC2": "SC2", "SARS-COV-2": "SC2"},  ‚Üì
  
  "faixas_ct": {                                       ‚Üê ABA 3: Faixas CT
    "detect_max": 38.0,                                ‚Üì
    "inconc_min": 38.01,
    "inconc_max": 40.0,
    "rp_min": 15.0,
    "rp_max": 35.0
  },
  
  "rps": ["RP", "RP_1", "RP_2"],                      ‚Üê ABA 4: RP
                                                        ‚Üì
  "export_fields": [                                   ‚Üê ABA 5: Export
    "Sars-Cov-2", "Influenzaa", ...                   ‚Üì
  ],
  
  "panel_tests_id": "1",
  "controles": {                                       ‚Üê ABA 6: Controles
    "cn": ["G11+G12"],                                 ‚Üì
    "cp": ["H11+H12"]
  },
  
  "comentarios": "Exame respirat√≥rio VR1e2; ...",
  "versao_protocolo": ""
}
```

**Arquivo 3: Padr√£o de UI Existente** (5 min)
- Local: `services/cadastros_diversos.py:1-80`
- **UI atual usa:**
  - `tk.Toplevel` window (modal)
  - `ttk.Treeview` para listbox de registros
  - `ctk.CTkEntry` para campos texto
  - `ctk.CTkLabel` para labels
  - `ctk.CTkButton` para a√ß√µes
  - CSV I/O com `csv.DictReader/DictWriter`

---

## üß† ENTENDIMENTO: 5 Conceitos Cr√≠ticos

### 1Ô∏è‚É£ **ExamConfig = Schema definido**

**O que √©:**
Uma `@dataclass` com 15 campos fixos. Voc√™ N√ÉO pode adicionar campos novos (seria quebra de contrato).

**Consequ√™ncia para UI:**
- Seu formul√°rio tem **exatamente 15 abas de entrada** (13-14 reais, 1-2 auto-calculados)
- N√£o pode criar campos extras
- Valida√ß√£o deve verificar tipos corretos

**Exemplo OK:**
```python
cfg = ExamConfig(
    nome_exame="VR1e2 Bio 7500",      # str ‚úì
    slug="vr1e2_bio_7500",             # str ‚úì
    equipamento="7500 Real-Time",      # str ‚úì
    faixas_ct={"detect_max": 38.0},    # Dict[str, float] ‚úì
    ...
)
```

**Exemplo ERRADO:**
```python
cfg.novo_campo = "algo"  # ‚ùå Quebra contrato
```

### 2Ô∏è‚É£ **Registry Hybrid Load = CSV + JSON**

**Fluxo:**
```
1. Carrega exames_config.csv (base de dados)
   ‚îî‚îÄ Todos exames t√™m entrada em CSV

2. Carrega config/exams/*.json (override)
   ‚îî‚îÄ Alguns exames t√™m configura√ß√µes em JSON

3. MERGE:
   - Se exame tem JSON ‚Üí Use JSON (sobrescreve CSV)
   - Se exame s√≥ tem CSV ‚Üí Use CSV
   - Se tem JSON sem CSV ‚Üí Apenas JSON (novo exame?)
```

**Implica√ß√£o para seu c√≥digo:**
- Quando salvar novo exame ‚Üí Save **apenas em JSON** (`config/exams/{slug}.json`)
- Depois chamar `registry.load()` para recarregar
- UI reflete novo estado

### 3Ô∏è‚É£ **Valida√ß√£o de Schema = Tipo-checking**

**O que validar:**
```python
def validate_exam(cfg: ExamConfig) -> Tuple[bool, str]:
    """Retorna (is_valid, mensagem_erro)"""
    
    # Verificar tipos
    if not isinstance(cfg.nome_exame, str) or not cfg.nome_exame.strip():
        return False, "nome_exame deve ser string n√£o-vazia"
    
    if not isinstance(cfg.faixas_ct, dict):
        return False, "faixas_ct deve ser Dict[str, float]"
    
    # Verificar ranges
    if cfg.faixas_ct.get("detect_max", 0) >= 50:
        return False, "detect_max deve ser < 50"
    
    # Verificar listas
    if not isinstance(cfg.alvos, list):
        return False, "alvos deve ser lista"
    
    return True, "OK"
```

**Regra de Ouro:**
- Se valida√ß√£o falhar ‚Üí N√£o salve
- Exiba erro claro no UI
- Permite usu√°rio corrigir

### 4Ô∏è‚É£ **Fluxo Novo Exame (vis√£o t√©cnica)**

```
1. User clica [Novo] na aba "Exames (Registry)"
   ‚Üì
2. ExamFormDialog(mode="novo") abre
   ‚îú‚îÄ Aba 1: Campos vazios
   ‚îú‚îÄ Aba 2: Campos vazios
   ‚îî‚îÄ ... Aba 6: Campos vazios
   ‚Üì
3. User preenche 6 abas (13+ campos)
   ‚Üì
4. User clica [Salvar]
   ‚îú‚îÄ _collect_form_data() ‚Üí ExamConfig
   ‚îú‚îÄ validate_exam(cfg) ‚Üí Ok?
   ‚îÇ  ‚îú‚îÄ SIM: continue
   ‚îÇ  ‚îî‚îÄ N√ÉO: exiba erro, return
   ‚îú‚îÄ slug = auto-gerado (nome_exame.lower().replace(...))
   ‚îú‚îÄ JSON path = config/exams/{slug}.json
   ‚îú‚îÄ Save JSON (json.dump)
   ‚îú‚îÄ registry.load() ‚Üê Recarrega tudo
   ‚îî‚îÄ callback(slug) ‚Üê Avisa UI
   ‚Üì
5. UI (listbox) recarrega ‚Üí novo exame vis√≠vel
```

### 5Ô∏è‚É£ **Mapeamento: Campo ‚Üí Widget ‚Üí Tipo**

**Planejamento de abas e widgets:**

```
ABA 1: B√ÅSICO (6 campos)
‚îú‚îÄ nome_exame       ‚Üí CTkEntry (str)
‚îú‚îÄ slug             ‚Üí CTkLabel (auto-read-only, gerado de nome_exame)
‚îú‚îÄ equipamento      ‚Üí CTkCombobox (dropdown de equipamentos conhecidos)
‚îú‚îÄ tipo_placa       ‚Üí CTkEntry (str, ex: "48")
‚îú‚îÄ esquema_grupo    ‚Üí CTkEntry (str, ex: "96->48")
‚îî‚îÄ kit_codigo       ‚Üí CTkEntry (int)

ABA 2: ALVOS (2 campos)
‚îú‚îÄ alvos            ‚Üí CTkTextbox (multi-linha, list JSON)
‚îî‚îÄ mapa_alvos       ‚Üí CTkTextbox (multi-linha, dict JSON)

ABA 3: FAIXAS CT (5 campos)
‚îú‚îÄ detect_max       ‚Üí CTkEntry (float)
‚îú‚îÄ inconc_min       ‚Üí CTkEntry (float)
‚îú‚îÄ inconc_max       ‚Üí CTkEntry (float)
‚îú‚îÄ rp_min           ‚Üí CTkEntry (float)
‚îî‚îÄ rp_max           ‚Üí CTkEntry (float)

ABA 4: RP (1 campo)
‚îî‚îÄ rps              ‚Üí CTkTextbox (multi-linha, list JSON)

ABA 5: EXPORT (2 campos)
‚îú‚îÄ export_fields    ‚Üí CTkTextbox (multi-linha, list JSON)
‚îî‚îÄ panel_tests_id   ‚Üí CTkEntry (str, ex: "1")

ABA 6: CONTROLES (2 campos + extras)
‚îú‚îÄ controles[cn]    ‚Üí CTkTextbox (multi-linha, list JSON, ex: ["G11+G12"])
‚îú‚îÄ controles[cp]    ‚Üí CTkTextbox (multi-linha, list JSON, ex: ["H11+H12"])
‚îú‚îÄ comentarios      ‚Üí CTkTextbox (multi-linha, texto livre)
‚îî‚îÄ versao_protocolo ‚Üí CTkEntry (str)
```

---

## üé® DESIGN: Layout da UI

### Sketch 1: Aba "Exames (Registry)" no TabView

```
‚îå‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îê
‚îÇ CadastrosDiversosWindow                                  ‚îÇ
‚îú‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚î§
‚îÇ [Exames] [Equipamentos] [Placas] [Regras]                ‚îÇ
‚îÇ [Exames (Registry)]  ‚Üê NEW ABA                          ‚îÇ
‚îú‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚î§
‚îÇ Status: Carregando... | Exame: VR1e2 Biomanguinhos 7500 ‚îÇ
‚îú‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚î§
‚îÇ Listbox (Exames):                                        ‚îÇ
‚îÇ ‚îå‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îê           ‚îÇ
‚îÇ ‚îÇ ‚úì VR1e2 Biomanguinhos 7500                ‚îÇ           ‚îÇ
‚îÇ ‚îÇ   ZDC Biomanguinhos 7500                  ‚îÇ           ‚îÇ
‚îÇ ‚îÇ   VR1                                      ‚îÇ           ‚îÇ
‚îÇ ‚îÇ   VR2                                      ‚îÇ           ‚îÇ
‚îÇ ‚îÇ   ... (scroll)                             ‚îÇ           ‚îÇ
‚îÇ ‚îî‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îò           ‚îÇ
‚îú‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚î§
‚îÇ Bot√µes:                                                  ‚îÇ
‚îÇ [Novo]  [Editar]  [Excluir]  [Recarregar]               ‚îÇ
‚îî‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îò
```

### Sketch 2: Dialog "Novo/Editar Exame" (ExamFormDialog)

```
‚îå‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îê
‚îÇ Novo Exame                                    [X]        ‚îÇ
‚îú‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚î§
‚îÇ [B√°sico] [Alvos] [Faixas] [RP] [Export] [Controles]    ‚îÇ
‚îú‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚î§
‚îÇ Tab: B√ÅSICO                                              ‚îÇ
‚îÇ                                                          ‚îÇ
‚îÇ Nome do Exame:  [VR1e2 Bio 7500___________]            ‚îÇ
‚îÇ Slug:           [vr1e2_bio_7500]  (read-only)          ‚îÇ
‚îÇ Equipamento:    [7500 Real-Time  ‚ñº]                    ‚îÇ
‚îÇ Tipo Placa:     [48_________]                          ‚îÇ
‚îÇ Esquema:        [96->48___________]                    ‚îÇ
‚îÇ Kit C√≥digo:     [1140_______]                          ‚îÇ
‚îú‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚î§
‚îÇ                        [Salvar]  [Cancelar]              ‚îÇ
‚îî‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îò
```

### Sketch 3: Dialog Aba "Alvos"

```
‚îå‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îê
‚îÇ Novo Exame                                    [X]        ‚îÇ
‚îú‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚î§
‚îÇ [B√°sico] [Alvos] [Faixas] [RP] [Export] [Controles]    ‚îÇ
‚îú‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚î§
‚îÇ Tab: ALVOS                                               ‚îÇ
‚îÇ                                                          ‚îÇ
‚îÇ Alvos (JSON list, um por linha ou JSON):                ‚îÇ
‚îÇ ‚îå‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îê        ‚îÇ
‚îÇ ‚îÇ["SC2", "HMPV", "INF A", "INF B", "ADV", ... ‚îÇ        ‚îÇ
‚îÇ ‚îÇ                                              ‚îÇ        ‚îÇ
‚îÇ ‚îî‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îò        ‚îÇ
‚îÇ                                                          ‚îÇ
‚îÇ Mapa Alvos (JSON dict):                                 ‚îÇ
‚îÇ ‚îå‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îê        ‚îÇ
‚îÇ ‚îÇ{"SC2": "SC2", "SARS-COV-2": "SC2", "HMPV": ‚îÇ        ‚îÇ
‚îÇ ‚îÇ"HMPV", "INFA": "INF A", ...}                 ‚îÇ        ‚îÇ
‚îÇ ‚îÇ                                              ‚îÇ        ‚îÇ
‚îÇ ‚îî‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îò        ‚îÇ
‚îú‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚î§
‚îÇ                        [Salvar]  [Cancelar]              ‚îÇ
‚îî‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îÄ‚îò
```

---

## üìã CHECKLIST ETAPA 1

```
‚úÖ LEITURA (15 min):
  [‚úì] Revisar ExamConfig dataclass (15 campos)
  [‚úì] Entender JSON exemplo (vr1e2_biomanguinhos_7500.json)
  [‚úì] Ver padr√£o UI atual (cadastros_diversos.py)
  [‚úì] Ler este arquivo (ETAPA1_PREPARACAO.md)

‚úÖ ENTENDIMENTO (20 min):
  [ ] Conceito 1: ExamConfig = Schema fixo
  [ ] Conceito 2: Registry Hybrid Load (CSV+JSON)
  [ ] Conceito 3: Valida√ß√£o de Schema
  [ ] Conceito 4: Fluxo Novo Exame (5 passos)
  [ ] Conceito 5: Mapeamento Campo‚ÜíWidget‚ÜíTipo

‚úÖ DESIGN (25 min):
  [ ] Copie sketches (Sketch 1, 2, 3) para papel/digital
  [ ] Defina tamanho da janela (ExamFormDialog)
  [ ] Defina alturas de Textbox (alvos, mapa_alvos, rps, export, controles)
  [ ] Decida: CTkEntry vs CTkCombobox para equipamento
  [ ] Decida: Como parse/display JSON em widgets?

‚úÖ DECIS√ïES T√âCNICAS:
  [ ] JSON parsing: Usar json.loads() ou YAML?
  [ ] Slug gera√ß√£o: "Nome Exame" ‚Üí "nome_exame"?
  [ ] Equipamentos dropdown: Donde vem a lista?
  [ ] Controles: Como exibir cn/cp em UI?
  [ ] Error messages: Portugu√™s ou Ingl√™s?

‚úÖ CODIFICA√á√ÉO PREPARAT√ìRIA:
  [ ] Criar classe RegistryExamEditor (skeleton ETAPA 2)
  [ ] Criar classe ExamFormDialog (skeleton ETAPA 4)
  [ ] Definir m√©todos necess√°rios
  [ ] Definir assinaturas de fun√ß√£o
```

---

## üéØ PR√ìXIMOS PASSOS (Fim de ETAPA 1)

1. **Leia este arquivo** (ETAPA1_PREPARACAO.md) ‚Äî 10 min
2. **Revise os 5 conceitos** ‚Äî 20 min
3. **Estude os sketches** ‚Äî 10 min
4. **Responda decis√µes t√©cnicas** ‚Äî 15 min
5. **Pronto para ETAPA 2!** ‚Äî ‚úÖ

---

## üìû D√öVIDAS FREQUENTES

**P: "Como gero o slug automaticamente?"**  
R: 
```python
def _generate_slug(nome_exame: str) -> str:
    return nome_exame.lower().replace(" ", "_").replace("-", "_").replace(".", "")
```

**P: "Como validar um JSON em CTkTextbox?"**  
R:
```python
import json
try:
    data = json.loads(textbox.get("1.0", tk.END))
    # OK
except json.JSONDecodeError as e:
    messagebox.showerror("Erro JSON", str(e))
```

**P: "Quantas linhas tem CTkTextbox?"**  
R: Voc√™ define na altura. Ex: `height=150` pixels ‚âà 8-10 linhas.

**P: "Como carregar equipamentos do CSV?"**  
R:
```python
def _load_equipamentos() -> List[str]:
    with open("banco/equipamentos.csv") as f:
        reader = csv.DictReader(f)
        return [row["nome"] for row in reader]
```

---

**Status:** ‚öôÔ∏è Em Prepara√ß√£o  
**Pr√≥xima:** ETAPA 2 (RegistryExamEditor class)  
**ETA:** ~2 horas  

