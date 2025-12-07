# üéØ ETAPA 4 ‚Äî Formul√°rio Multi-Aba
**Status:** IN PROGRESS  
**Tempo:** ~3 horas  
**Data:** 2025-12-07  

---

## üìã O que vai ser implementado

Classe **ExamFormDialog** com:

### 6 Abas + 13 campos:

```
ABA 1: B√ÅSICO (6 campos)
‚îú‚îÄ nome_exame       ‚Üí CTkEntry (str, obrigat√≥rio)
‚îú‚îÄ slug             ‚Üí CTkLabel (read-only, auto-gerado)
‚îú‚îÄ equipamento      ‚Üí CTkCombobox (dropdown)
‚îú‚îÄ tipo_placa       ‚Üí CTkEntry (str)
‚îú‚îÄ esquema_grupo    ‚Üí CTkEntry (str)
‚îî‚îÄ kit_codigo       ‚Üí CTkEntry (int)

ABA 2: ALVOS (2 campos)
‚îú‚îÄ alvos            ‚Üí CTkTextbox (multi-linha, JSON list)
‚îî‚îÄ mapa_alvos       ‚Üí CTkTextbox (multi-linha, JSON dict)

ABA 3: FAIXAS CT (5 campos)
‚îú‚îÄ detect_max       ‚Üí CTkEntry (float)
‚îú‚îÄ inconc_min       ‚Üí CTkEntry (float)
‚îú‚îÄ inconc_max       ‚Üí CTkEntry (float)
‚îú‚îÄ rp_min           ‚Üí CTkEntry (float)
‚îî‚îÄ rp_max           ‚Üí CTkEntry (float)

ABA 4: RP (1 campo)
‚îî‚îÄ rps              ‚Üí CTkTextbox (multi-linha, JSON list)

ABA 5: EXPORT (2 campos)
‚îú‚îÄ export_fields    ‚Üí CTkTextbox (multi-linha, JSON list)
‚îî‚îÄ panel_tests_id   ‚Üí CTkEntry (str)

ABA 6: CONTROLES (3 campos + 2 extras)
‚îú‚îÄ controles[cn]    ‚Üí CTkTextbox (JSON list)
‚îú‚îÄ controles[cp]    ‚Üí CTkTextbox (JSON list)
‚îú‚îÄ comentarios      ‚Üí CTkTextbox (multi-linha)
‚îî‚îÄ versao_protocolo ‚Üí CTkEntry (str)
```

### M√©todos:
- `__init__(parent, cfg=None)` ‚Äî Novo ou editar (cfg preenchido)
- `_build_tab_basico()` ‚Äî 6 campos entrada
- `_build_tab_alvos()` ‚Äî alvos + mapa
- `_build_tab_faixas()` ‚Äî 5 floats
- `_build_tab_rp()` ‚Äî lista RP
- `_build_tab_export()` ‚Äî export_fields + panel_id
- `_build_tab_controles()` ‚Äî CN/CP + comentarios + versao
- `_collect_form_data()` ‚Üí ExamConfig
- `_salvar()` ‚Üí validar + save + callback

---

## üèóÔ∏è Estrutura da classe

```python
class ExamFormDialog:
    """Dialog para criar/editar exame com 6 abas"""
    
    def __init__(self, parent, cfg=None, on_save=None):
        self.parent = parent
        self.cfg = cfg  # None se novo, ExamConfig se editando
        self.on_save = on_save  # Callback ap√≥s salvar
        self.editor = RegistryExamEditor()
        
        self.window = tk.Toplevel(parent)
        self.window.title("Novo Exame" if not cfg else f"Editar: {cfg.nome_exame}")
        self.window.geometry("900x700")
        
        # State
        self._equipamentos = self._load_equipamentos()
        
        self._build_ui()
    
    def _build_ui(self):
        # CTkTabview com 6 abas
        # CTkFrame com bot√µes [Salvar] [Cancelar]
    
    def _build_tab_*()...  # x6 m√©todos
    
    def _collect_form_data() -> ExamConfig:
        # Coleta dados de todas as abas
    
    def _salvar(self):
        # Validar + save_exam + reload + callback
```

---

## üîß Pr√≥ximos passos

1. Criar classe ExamFormDialog (ser√° grande ~400 linhas)
2. Integrar com bot√µes [Novo] e [Editar] da ETAPA 3
3. Testar abertura de dialog
4. Testar form data collection
5. Testar valida√ß√£o antes de salvar

**Tempo estimado:** 3 horas (implementa√ß√£o + debug)

