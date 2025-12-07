# ğŸ“‹ PLANO DE IMPLEMENTAÃ‡ÃƒO â€” FASE 5 (UI de Cadastro/EdiÃ§Ã£o)

**Objetivo:** Completar Fase 5 em ~11-12 horas  
**Resultado Final:** Tela "Gerenciar Exames" com registry integration completa

---

## ğŸ�¯ VISÃƒO GERAL DO PLANO

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�
â”‚ FASE 5 â€” Plano em 6 Etapas (11-12 horas totais)               â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                 â”‚
â”‚ ETAPA 1: PreparaÃ§Ã£o & Design (1-2h)                           â”‚
â”‚   â””â”€ Revisar cÃ³digo + schema + requirements                    â”‚
â”‚                                                                 â”‚
â”‚ ETAPA 2: Classe RegistryExamEditor (2h)                       â”‚
â”‚   â””â”€ Load/Save/Validate ExamConfig                             â”‚
â”‚                                                                 â”‚
â”‚ ETAPA 3: UI Aba "Exames (Registry)" (2h)                      â”‚
â”‚   â””â”€ Listbox + Buttons (Novo, Editar, Excluir)                â”‚
â”‚                                                                 â”‚
â”‚ ETAPA 4: FormulÃ¡rio Multi-Aba (3h)                            â”‚
â”‚   â””â”€ 6 abas com 13+ campos + widgets                           â”‚
â”‚                                                                 â”‚
â”‚ ETAPA 5: IntegraÃ§Ã£o JSON + Registry Reload (2h)               â”‚
â”‚   â””â”€ Save JSON + registry.load() + UI refresh                  â”‚
â”‚                                                                 â”‚
â”‚ ETAPA 6: ValidaÃ§Ã£o, Testes & Polimento (1-2h)                â”‚
â”‚   â””â”€ Schema validation + testes + tratamento erros             â”‚
â”‚                                                                 â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## ğŸ“Š ETAPA 1: PreparaÃ§Ã£o & Design (1-2 horas)

### 1.1 Revisar & Entender

**Ler:**
- [ ] `RELATORIO_FASE5_ANALISE.md` (seÃ§Ãµes 1-4)
- [ ] `MAPA_VISUAL_FASE5.md` (fluxos)
- [ ] `services/exam_registry.py` (linhas 55-90, ExamConfig)

**Entender:**
- [ ] ExamConfig dataclass (15 campos)
- [ ] normalize_target() method
- [ ] bloco_size() method
- [ ] Estrutura de `config/exams/<slug>.json`

### 1.2 Revisar CÃ³digo Existente

**Ler:**
- [ ] `services/cadastros_diversos.py` (completo, 905 linhas)
- [ ] `services/menu_handler.py` (integraÃ§Ã£o)
- [ ] `config/exams/vr1e2_*.json` e `zdc_*.json` (exemplos)

**Entender:**
- [ ] Como funciona CadastrosDiversosWindow
- [ ] PadrÃ£o de _build_tab_* e _load_csv/_save_csv
- [ ] Estrutura de eventos (seleÃ§Ã£o, novo, salvar)

### 1.3 Design da Nova Aba

**Sketchar:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�
â”‚ [Novo]  [Editar]  [Excluir]  [Recarregar Registry]    â”‚
â”‚                                                        â”‚
â”‚ Exames (Registry):                                     â”‚
â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�              â”‚
â”‚ â”‚ â€¢ VR1e2 Biomanguinhos 7500          â”‚              â”‚
â”‚ â”‚ â€¢ ZDC Biomanguinhos 7500            â”‚              â”‚
â”‚ â”‚ â€¢ VR1                               â”‚              â”‚
â”‚ â”‚ â€¢ VR2                               â”‚              â”‚
â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜              â”‚
â”‚                                                        â”‚
â”‚ Status: [Nenhum exame selecionado]                    â”‚
â”‚                                                        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Checklist Etapa 1:**
- [ ] Entendimento de ExamConfig
- [ ] Conhecimento do cÃ³digo existente
- [ ] Design da nova aba esboÃ§ado

---

## ğŸ�—ï¸� ETAPA 2: Classe RegistryExamEditor (2 horas)

### 2.1 Criar Classe Auxiliar

**Arquivo:** `services/cadastros_diversos.py` (adicionar no topo, antes de CadastrosDiversosWindow)

**CÃ³digo:**
```python
@dataclass
class RegistryExamEditor:
    """Gerencia ediÃ§Ã£o de exames via Registry"""
    
    def load_exam(self, slug: str) -> Optional[ExamConfig]:
        """Carrega exame do registry pelo slug"""
        from services.exam_registry import get_exam_cfg
        cfg = get_exam_cfg(slug)
        return cfg if cfg.alvos else None  # None se fallback
    
    def load_all_exams(self) -> List[Tuple[str, str]]:
        """Retorna lista de (nome_exame, slug) do registry"""
        from services.exam_registry import registry
        result = []
        for key, cfg in registry.exams.items():
            result.append((cfg.nome_exame, cfg.slug))
        return sorted(result)
    
    def save_exam(self, exam_cfg: ExamConfig) -> Tuple[bool, str]:
        """Salva ExamConfig em config/exams/{slug}.json"""
        import json
        from pathlib import Path
        
        try:
            # Validar antes de salvar
            valid, msg = self.validate_exam(exam_cfg)
            if not valid:
                return False, msg
            
            # Criar diretÃ³rio se nÃ£o existir
            exams_dir = BASE_DIR / "config" / "exams"
            exams_dir.mkdir(parents=True, exist_ok=True)
            
            # Serializar para dict
            exam_dict = self._exam_to_dict(exam_cfg)
            
            # Salvar JSON
            slug = exam_cfg.slug
            json_file = exams_dir / f"{slug}.json"
            json_file.write_text(json.dumps(exam_dict, indent=2, ensure_ascii=False), encoding="utf-8")
            
            registrar_log("RegistryExamEditor", f"Exame salvo: {json_file}", "INFO")
            return True, f"Exame '{exam_cfg.nome_exame}' salvo com sucesso!"
            
        except Exception as e:
            registrar_log("RegistryExamEditor", f"Erro ao salvar: {e}", "ERROR")
            return False, f"Erro ao salvar exame: {e}"
    
    def delete_exam(self, slug: str) -> Tuple[bool, str]:
        """Deleta exame (arquivo JSON)"""
        from pathlib import Path
        
        try:
            json_file = BASE_DIR / "config" / "exams" / f"{slug}.json"
            if json_file.exists():
                json_file.unlink()
                registrar_log("RegistryExamEditor", f"Exame deletado: {json_file}", "INFO")
                return True, f"Exame '{slug}' deletado com sucesso!"
            return False, "Arquivo JSON nÃ£o encontrado"
        except Exception as e:
            registrar_log("RegistryExamEditor", f"Erro ao deletar: {e}", "ERROR")
            return False, f"Erro ao deletar exame: {e}"
    
    def validate_exam(self, exam_cfg: ExamConfig) -> Tuple[bool, str]:
        """Valida schema ExamConfig"""
        errors = []
        
        # Campos obrigatÃ³rios
        if not exam_cfg.nome_exame or not exam_cfg.nome_exame.strip():
            errors.append("â€¢ Nome do exame Ã© obrigatÃ³rio")
        if not exam_cfg.slug or not exam_cfg.slug.strip():
            errors.append("â€¢ Slug Ã© obrigatÃ³rio")
        if not exam_cfg.tipo_placa_analitica:
            errors.append("â€¢ Tipo de placa Ã© obrigatÃ³rio")
        
        # Faixas CT
        faixas = exam_cfg.faixas_ct
        if faixas:
            detect_max = faixas.get("detect_max", 38.0)
            inconc_min = faixas.get("inconc_min", 38.01)
            inconc_max = faixas.get("inconc_max", 40.0)
            rp_min = faixas.get("rp_min", 15.0)
            rp_max = faixas.get("rp_max", 35.0)
            
            if detect_max >= inconc_min:
                errors.append(f"â€¢ detect_max ({detect_max}) deve ser < inconc_min ({inconc_min})")
            if inconc_min > inconc_max:
                errors.append(f"â€¢ inconc_min ({inconc_min}) deve ser <= inconc_max ({inconc_max})")
            if rp_min >= rp_max:
                errors.append(f"â€¢ rp_min ({rp_min}) deve ser < rp_max ({rp_max})")
        
        # Alvos
        if not exam_cfg.alvos or len(exam_cfg.alvos) == 0:
            errors.append("â€¢ Alvos nÃ£o podem estar vazios")
        
        if errors:
            return False, "Erros de validaÃ§Ã£o:\n" + "\n".join(errors)
        return True, "Exame vÃ¡lido"
    
    def reload_registry(self) -> None:
        """Recarrega registry apÃ³s mudanÃ§as"""
        from services import exam_registry
        exam_registry.registry.load()
        registrar_log("RegistryExamEditor", "Registry recarregado", "INFO")
    
    @staticmethod
    def _exam_to_dict(cfg: ExamConfig) -> Dict[str, Any]:
        """Converte ExamConfig para dict para JSON serialization"""
        return {
            "nome_exame": cfg.nome_exame,
            "slug": cfg.slug,
            "equipamento": cfg.equipamento,
            "tipo_placa_analitica": cfg.tipo_placa_analitica,
            "esquema_agrupamento": cfg.esquema_agrupamento,
            "kit_codigo": cfg.kit_codigo,
            "alvos": cfg.alvos,
            "mapa_alvos": cfg.mapa_alvos,
            "faixas_ct": cfg.faixas_ct,
            "rps": cfg.rps,
            "export_fields": cfg.export_fields,
            "panel_tests_id": cfg.panel_tests_id,
            "controles": cfg.controles,
            "comentarios": cfg.comentarios,
            "versao_protocolo": cfg.versao_protocolo,
        }
```

**Checklist Etapa 2:**
- [ ] Classe RegistryExamEditor criada
- [ ] Todos os 7 mÃ©todos implementados
- [ ] ImportaÃ§Ãµes adicionadas
- [ ] ValidaÃ§Ã£o de schema completa

---

## ğŸ�¨ ETAPA 3: UI Aba "Exames (Registry)" (2 horas)

### 3.1 Adicionar Aba ao TabView

**LocalizaÃ§Ã£o:** `services/cadastros_diversos.py`

**Em `_build_ui()`, apÃ³s criar outras abas:**
```python
self.tab_exames_registry = self.tabview.add("Exames (Registry)")
self._build_tab_exames_registry()
```

### 3.2 Implementar `_build_tab_exames_registry()`

**CÃ³digo (~100 linhas):**
```python
def _build_tab_exames_registry(self) -> None:
    """ConstrÃ³i aba de gerenciamento de exames (registry JSON)"""
    frame = ctk.CTkFrame(self.tab_exames_registry)
    frame.pack(expand=True, fill="both", padx=10, pady=10)
    
    # TÃ­tulo
    title = ctk.CTkLabel(
        frame,
        text="Gerenciar Exames (Registry)",
        font=ctk.CTkFont(size=16, weight="bold"),
    )
    title.pack(pady=(0, 10))
    
    # BotÃµes de aÃ§Ã£o
    btn_frame = ctk.CTkFrame(frame)
    btn_frame.pack(fill="x", padx=5, pady=(0, 10))
    
    ctk.CTkButton(
        btn_frame,
        text="Novo",
        command=self._novo_exame_registry,
        width=80,
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        btn_frame,
        text="Editar",
        command=self._editar_exame_registry,
        width=80,
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        btn_frame,
        text="Excluir",
        command=self._excluir_exame_registry,
        width=80,
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        btn_frame,
        text="Recarregar Registry",
        command=self._recarregar_registry,
        width=150,
    ).pack(side="right", padx=5)
    
    # Listbox com exames
    list_frame = ctk.CTkFrame(frame)
    list_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    list_label = ctk.CTkLabel(
        list_frame,
        text="Exames Carregados:",
        font=ctk.CTkFont(size=12, weight="bold"),
    )
    list_label.pack(anchor="w", pady=(0, 5))
    
    self.listbox_exames_registry = tk.Listbox(
        list_frame,
        font=("Arial", 10),
        height=12,
    )
    self.listbox_exames_registry.pack(fill="both", expand=True)
    self.listbox_exames_registry.bind("<<ListboxSelect>>", self._on_select_exam_registry)
    
    # Status
    self.status_registry = ctk.CTkLabel(
        frame,
        text="Nenhum exame selecionado",
        font=ctk.CTkFont(size=10),
        text_color="gray",
    )
    self.status_registry.pack(pady=(10, 0), anchor="w", padx=5)
    
    # Carregar lista inicial
    self.editor_registry = RegistryExamEditor()
    self._carregar_exames_registry()
```

### 3.3 Implementar Callbacks

**MÃ©todos (~80 linhas):**
```python
def _carregar_exames_registry(self) -> None:
    """Carrega lista de exames do registry no listbox"""
    self.listbox_exames_registry.delete(0, "end")
    self.current_exam_registry = None
    self.status_registry.configure(text="Nenhum exame selecionado")
    
    try:
        exames = self.editor_registry.load_all_exams()
        for nome, slug in exames:
            self.listbox_exames_registry.insert("end", nome)
    except Exception as e:
        registrar_log("CadastrosDiversos", f"Erro ao carregar registry: {e}", "ERROR")
        self.status_registry.configure(text=f"Erro: {e}", text_color="red")

def _on_select_exam_registry(self, event=None) -> None:
    """Seleciona exame no listbox"""
    sel = self.listbox_exames_registry.curselection()
    if not sel:
        return
    idx = sel[0]
    exames = self.editor_registry.load_all_exams()
    if idx < len(exames):
        nome, slug = exames[idx]
        self.current_exam_registry = slug
        self.status_registry.configure(
            text=f"Selecionado: {nome} (slug: {slug})",
            text_color="green",
        )

def _novo_exame_registry(self) -> None:
    """Abre formulÃ¡rio para novo exame"""
    self.current_exam_registry = None
    self._abrir_formulario_exame()

def _editar_exame_registry(self) -> None:
    """Abre formulÃ¡rio para editar exame selecionado"""
    if not self.current_exam_registry:
        messagebox.showwarning(
            "Aviso",
            "Selecione um exame para editar.",
            parent=self.window,
        )
        return
    self._abrir_formulario_exame(self.current_exam_registry)

def _excluir_exame_registry(self) -> None:
    """Deleta exame selecionado"""
    if not self.current_exam_registry:
        messagebox.showwarning(
            "Aviso",
            "Selecione um exame para excluir.",
            parent=self.window,
        )
        return
    
    if not messagebox.askyesno(
        "ConfirmaÃ§Ã£o",
        f"Deseja realmente excluir '{self.current_exam_registry}'?",
        parent=self.window,
    ):
        return
    
    success, msg = self.editor_registry.delete_exam(self.current_exam_registry)
    if success:
        self.editor_registry.reload_registry()
        self._carregar_exames_registry()
        messagebox.showinfo("Sucesso", msg, parent=self.window)
    else:
        messagebox.showerror("Erro", msg, parent=self.window)

def _recarregar_registry(self) -> None:
    """Recarrega registry e atualiza listbox"""
    self.editor_registry.reload_registry()
    self._carregar_exames_registry()
    messagebox.showinfo("Sucesso", "Registry recarregado!", parent=self.window)
```

**Checklist Etapa 3:**
- [ ] Aba "Exames (Registry)" adicionada ao TabView
- [ ] Listbox com exames do registry
- [ ] BotÃµes: Novo, Editar, Excluir, Recarregar
- [ ] MÃ©todos de callback implementados
- [ ] Status label mostrando seleÃ§Ã£o

---

## ğŸ“� ETAPA 4: FormulÃ¡rio Multi-Aba (3 horas)

### 4.1 Criar Toplevel Window para FormulÃ¡rio

**MÃ©todo em CadastrosDiversosWindow (~400 linhas):**
```python
def _abrir_formulario_exame(self, slug: Optional[str] = None) -> None:
    """Abre janela com formulÃ¡rio multi-aba para novo/editar exame"""
    
    # Carregar exame se editando
    exam_cfg = None
    if slug:
        exam_cfg = self.editor_registry.load_exam(slug)
        if not exam_cfg:
            messagebox.showerror("Erro", f"Exame '{slug}' nÃ£o encontrado")
            return
    
    # Criar janela
    form_window = tk.Toplevel(self.window)
    form_window.title("Novo Exame" if not exam_cfg else f"Editar {exam_cfg.nome_exame}")
    form_window.geometry("700x600")
    form_window.transient(self.window)
    form_window.grab_set()
    
    # Criar ExamFormDialog
    ExamFormDialog(form_window, exam_cfg, self._on_exame_salvo)
```

### 4.2 Criar Classe ExamFormDialog

**Nova classe em cadastros_diversos.py (~350 linhas):**
```python
class ExamFormDialog:
    """DiÃ¡logo para ediÃ§Ã£o de exame com 6 abas"""
    
    def __init__(self, parent_window: tk.Toplevel, exam_cfg: Optional[ExamConfig], callback):
        self.parent_window = parent_window
        self.exam_cfg = exam_cfg or self._create_default_config()
        self.callback = callback
        self.editor = RegistryExamEditor()
        
        self._build_ui()
    
    def _build_ui(self) -> None:
        """ConstrÃ³i UI multi-aba"""
        main_frame = ctk.CTkFrame(self.parent_window)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # TabView com 6 abas
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(expand=True, fill="both", pady=(0, 10))
        
        self.tab_basico = self.tabview.add("BÃ¡sico")
        self.tab_alvos = self.tabview.add("Alvos")
        self.tab_faixas = self.tabview.add("Faixas CT")
        self.tab_rp = self.tabview.add("RP")
        self.tab_export = self.tabview.add("Export")
        self.tab_controles = self.tabview.add("Controles")
        
        self._build_tab_basico()
        self._build_tab_alvos()
        self._build_tab_faixas()
        self._build_tab_rp()
        self._build_tab_export()
        self._build_tab_controles()
        
        # BotÃµes
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(fill="x", pady=(0, 0))
        
        ctk.CTkButton(
            btn_frame,
            text="Salvar",
            command=self._salvar,
            width=150,
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.parent_window.destroy,
            width=150,
        ).pack(side="right", padx=5)
    
    def _build_tab_basico(self) -> None:
        """ABA 1: Campos bÃ¡sicos (6 campos)"""
        # nome_exame, slug, equipamento, tipo_placa, esquema_agrupamento, kit_codigo
        # ~50 linhas com CTkEntry widgets
        pass  # Implementar
    
    def _build_tab_alvos(self) -> None:
        """ABA 2: Alvos + Mapa (2 campos)"""
        # alvos (lista), mapa_alvos (dicts)
        # ~60 linhas com Text widget + button para editar mapa
        pass  # Implementar
    
    def _build_tab_faixas(self) -> None:
        """ABA 3: Faixas CT (5 campos)"""
        # detect_max, inconc_min, inconc_max, rp_min, rp_max
        # ~50 linhas com CTkEntry (float validation)
        pass  # Implementar
    
    def _build_tab_rp(self) -> None:
        """ABA 4: RPs (1 campo)"""
        # rps (lista)
        # ~40 linhas com Text widget
        pass  # Implementar
    
    def _build_tab_export(self) -> None:
        """ABA 5: Export (2 campos)"""
        # export_fields (lista), panel_tests_id (string)
        # ~50 linhas com Text + Entry
        pass  # Implementar
    
    def _build_tab_controles(self) -> None:
        """ABA 6: Controles (2 campos)"""
        # controles.cn (lista), controles.cp (lista)
        # ~50 linhas com Text widgets
        pass  # Implementar
    
    def _salvar(self) -> None:
        """Valida, serializa e salva exame"""
        # Coletar dados de todas abas
        exam_cfg = self._collect_form_data()
        
        # Validar
        valid, msg = self.editor.validate_exam(exam_cfg)
        if not valid:
            messagebox.showerror("Erro de ValidaÃ§Ã£o", msg)
            return
        
        # Salvar
        success, msg = self.editor.save_exam(exam_cfg)
        if success:
            self.editor.reload_registry()
            messagebox.showinfo("Sucesso", msg)
            self.callback()  # Callback para atualizar listbox
            self.parent_window.destroy()
        else:
            messagebox.showerror("Erro", msg)
    
    def _collect_form_data(self) -> ExamConfig:
        """Coleta dados de todos os fields e retorna ExamConfig"""
        # Ler valores de todos CTkEntry/Text widgets
        pass  # Implementar
    
    def _create_default_config(self) -> ExamConfig:
        """Cria ExamConfig vazio para novo exame"""
        return ExamConfig(
            nome_exame="",
            slug="",
            equipamento="7500 Real-Time",
            tipo_placa_analitica="96",
            esquema_agrupamento="96->96",
            kit_codigo="",
            alvos=[],
            mapa_alvos={},
            faixas_ct={"detect_max": 38.0, "inconc_min": 38.01, "inconc_max": 40.0, "rp_min": 15.0, "rp_max": 35.0},
            rps=["RP"],
            export_fields=[],
            panel_tests_id="",
            controles={"cn": [], "cp": []},
        )
```

**Detalhe: Cada _build_tab_* deveria ter CTkLabel + widget para cada campo:**
```python
def _build_tab_basico(self) -> None:
    frame = ctk.CTkScrollableFrame(self.tab_basico)
    frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Nome Exame
    ctk.CTkLabel(frame, text="Nome Exame:").pack(anchor="w", pady=(10, 0))
    self.entry_nome = ctk.CTkEntry(frame)
    self.entry_nome.insert(0, self.exam_cfg.nome_exame)
    self.entry_nome.pack(fill="x", pady=(0, 10))
    
    # Slug (auto-generated ou editÃ¡vel)
    ctk.CTkLabel(frame, text="Slug:").pack(anchor="w", pady=(10, 0))
    self.entry_slug = ctk.CTkEntry(frame)
    self.entry_slug.insert(0, self.exam_cfg.slug)
    self.entry_slug.pack(fill="x", pady=(0, 10))
    
    # ... (repeater para outros 4 campos)
```

**Checklist Etapa 4:**
- [ ] Classe ExamFormDialog criada
- [ ] 6 abas implementadas com todos os campos
- [ ] Cada aba tem labels + widgets (Entry, Text, Combobox)
- [ ] Dados preenchidos se editando exame existente
- [ ] MÃ©todo _collect_form_data implementado
- [ ] MÃ©todo _salvar implementado

---

## ğŸ”„ ETAPA 5: IntegraÃ§Ã£o JSON + Registry Reload (2 horas)

### 5.1 Testar Save JSON

**MÃ©todo de teste:**
```python
def _on_exame_salvo(self) -> None:
    """Callback apÃ³s exame salvo"""
    self._carregar_exames_registry()
    self.status_registry.configure(text="Exame salvo com sucesso!", text_color="green")
```

### 5.2 Verificar Registry Reload

**VerificaÃ§Ã£o:**
```python
def _recarregar_registry(self) -> None:
    """Recarrega registry e atualiza listbox"""
    self.editor_registry.reload_registry()
    
    # Verificar se registry foi recarregado
    from services.exam_registry import registry
    count = len(registry.exams)
    
    self._carregar_exames_registry()
    messagebox.showinfo("Sucesso", f"Registry recarregado! ({count} exames)")
```

### 5.3 Testar Fluxo Completo

**Teste manual:**
1. Clique "Novo Exame"
2. Preencha 6 abas
3. Clique "Salvar"
4. Verificar: arquivo criado em `config/exams/<slug>.json`
5. Verificar: exame aparece no listbox
6. Clique "Recarregar Registry"
7. Verificar: registry atualizado

**Checklist Etapa 5:**
- [ ] RegistryExamEditor.save_exam() funciona
- [ ] JSON criado em `config/exams/<slug>.json`
- [ ] registry.load() atualiza dados
- [ ] Listbox atualizado apÃ³s salvar
- [ ] Recarregar Registry button funciona

---

## âœ… ETAPA 6: ValidaÃ§Ã£o, Testes & Polimento (1-2 horas)

### 6.1 Testes UnitÃ¡rios

**Criar `tests/test_fase5_registry_editor.py` (~150 linhas):**
```python
import pytest
from services.cadastros_diversos import RegistryExamEditor
from services.exam_registry import ExamConfig

def test_load_all_exams():
    """Testa carregamento de todos exames"""
    editor = RegistryExamEditor()
    exames = editor.load_all_exams()
    assert len(exames) > 0
    assert any("VR1e2" in nome for nome, _ in exames)

def test_validate_exam_valid():
    """Testa validaÃ§Ã£o de exame vÃ¡lido"""
    editor = RegistryExamEditor()
    cfg = ExamConfig(
        nome_exame="Test Exam",
        slug="test_exam",
        equipamento="7500 Real-Time",
        tipo_placa_analitica="96",
        esquema_agrupamento="96->96",
        kit_codigo="9999",
        alvos=["ALV1", "ALV2"],
        faixas_ct={"detect_max": 38.0, "inconc_min": 38.01, "inconc_max": 40.0, "rp_min": 15.0, "rp_max": 35.0},
    )
    valid, msg = editor.validate_exam(cfg)
    assert valid
    assert "vÃ¡lido" in msg.lower()

def test_validate_exam_invalid():
    """Testa validaÃ§Ã£o de exame invÃ¡lido"""
    editor = RegistryExamEditor()
    cfg = ExamConfig(
        nome_exame="",  # invÃ¡lido
        slug="test",
        equipamento="7500 Real-Time",
        tipo_placa_analitica="96",
        esquema_agrupamento="96->96",
        kit_codigo="",
        alvos=[],  # invÃ¡lido
    )
    valid, msg = editor.validate_exam(cfg)
    assert not valid
    assert "obrigatÃ³rio" in msg.lower()

def test_save_exam():
    """Testa salvar exame em JSON"""
    editor = RegistryExamEditor()
    cfg = ExamConfig(
        nome_exame="Test Exam",
        slug="test_exam_save",
        equipamento="7500 Real-Time",
        tipo_placa_analitica="96",
        esquema_agrupamento="96->96",
        kit_codigo="9999",
        alvos=["ALV1"],
        faixas_ct={"detect_max": 38.0, "inconc_min": 38.01, "inconc_max": 40.0, "rp_min": 15.0, "rp_max": 35.0},
    )
    success, msg = editor.save_exam(cfg)
    assert success
    # Verificar arquivo criado
    from pathlib import Path
    json_file = Path(__file__).parent.parent / "config" / "exams" / "test_exam_save.json"
    assert json_file.exists()

def test_delete_exam():
    """Testa deletar exame"""
    editor = RegistryExamEditor()
    success, msg = editor.delete_exam("test_exam_save")
    assert success
```

**Executar:**
```bash
pytest tests/test_fase5_registry_editor.py -v
```

### 6.2 Testes Manuais (IntegraÃ§Ã£o UI)

**Checklist:**
- [ ] BotÃ£o "Novo Exame" no menu funciona
- [ ] FormulÃ¡rio abre com 6 abas
- [ ] Abas navegÃ¡veis
- [ ] Novo exame â†’ JSON criado â†’ Registry recarregado â†’ Listbox atualizado
- [ ] Editar exame existente â†’ Campos preenchidos â†’ Salvar â†’ JSON atualizado
- [ ] Excluir exame â†’ ConfirmaÃ§Ã£o â†’ Arquivo removido â†’ Listbox atualizado
- [ ] ValidaÃ§Ã£o rejeita dados invÃ¡lidos
- [ ] Mensagens de erro legÃ­veis

### 6.3 Tratamento de Erros & Edge Cases

**Implementar:**
- [ ] Slug duplicado (avisar user)
- [ ] Arquivo JSON corrompido (error message)
- [ ] Registry vazio (mensagem informativa)
- [ ] PermissÃµes de arquivo (try/except)
- [ ] Caracteres especiais em nome (normalizar)

### 6.4 Polimento UI

**Melhorias:**
- [ ] Tooltips em campos obrigatÃ³rios
- [ ] Cores indicando campos invÃ¡lidos
- [ ] Spinner/loader durante save
- [ ] ConfirmaÃ§Ã£o ao fechar com dados nÃ£o salvos
- [ ] Help text em cada aba

**Checklist Etapa 6:**
- [ ] Testes unitÃ¡rios passam (pytest)
- [ ] Testes manuais passam (UI integraÃ§Ã£o)
- [ ] Edge cases tratados
- [ ] Mensagens de erro Ãºteis
- [ ] UI polida (tooltips, cores, feedback)

---

## ğŸ“… CRONOGRAMA RECOMENDADO

### Dia 1 (4 horas)

```
09:00 - 10:30 (1.5h):  ETAPA 1 â€” PreparaÃ§Ã£o & Design
                        â€¢ Ler documentaÃ§Ã£o
                        â€¢ Revisar cÃ³digo
                        â€¢ Entender schema

10:30 - 12:30 (2h):    ETAPA 2 â€” Classe RegistryExamEditor
                        â€¢ Implementar 7 mÃ©todos
                        â€¢ Testes de imports
                        
12:30 - 14:00 (1.5h):  ETAPA 3 â€” UI Aba "Exames (Registry)"
                        â€¢ Listbox + buttons
                        â€¢ Callbacks de seleÃ§Ã£o
```

### Dia 2 (4 horas)

```
09:00 - 12:00 (3h):    ETAPA 4 â€” FormulÃ¡rio Multi-Aba
                        â€¢ 6 abas com 13+ campos
                        â€¢ Data collection
                        
12:00 - 14:00 (2h):    ETAPA 5 â€” IntegraÃ§Ã£o JSON + Registry
                        â€¢ Save JSON
                        â€¢ Registry reload
                        â€¢ Testes bÃ¡sicos
```

### Dia 3 (3-4 horas)

```
09:00 - 10:30 (1.5h):  ETAPA 6 â€” Testes UnitÃ¡rios
                        â€¢ Pytest cases
                        â€¢ Edge cases
                        
10:30 - 12:30 (2h):    ETAPA 6 â€” Testes Manuais & Polimento
                        â€¢ UI testing
                        â€¢ Error handling
                        â€¢ Refinamento visual
                        
12:30 - 14:00 (1h):    FinalizaÃ§Ã£o
                        â€¢ DocumentaÃ§Ã£o atualizada
                        â€¢ TODO.md marcado completo
```

---

## ğŸ“‹ TAREFAS ESPECÃ�FICAS POR ETAPA

### âœ… ETAPA 1: PreparaÃ§Ã£o (1-2h)

- [ ] Ler `RELATORIO_FASE5_ANALISE.md` seÃ§Ãµes 1-4
- [ ] Ler `services/exam_registry.py` linhas 55-90
- [ ] Ler `services/cadastros_diversos.py` completo
- [ ] Entender ExamConfig dataclass
- [ ] Revisar `config/exams/vr1e2_*.json` exemplo
- [ ] Entender fluxo: Novo â†’ Form â†’ Validate â†’ Save JSON â†’ Reload Registry

### âœ… ETAPA 2: RegistryExamEditor (2h)

- [ ] Criar @dataclass RegistryExamEditor
- [ ] Implementar load_all_exams()
- [ ] Implementar load_exam(slug)
- [ ] Implementar save_exam(cfg)
- [ ] Implementar delete_exam(slug)
- [ ] Implementar validate_exam(cfg)
- [ ] Implementar reload_registry()
- [ ] Implementar _exam_to_dict()
- [ ] Testar imports (pytest)

### âœ… ETAPA 3: UI Aba Registry (2h)

- [ ] Adicionar aba ao TabView: `self.tabview.add("Exames (Registry)")`
- [ ] Criar _build_tab_exames_registry() (~120 linhas)
- [ ] Implementar botÃµes: Novo, Editar, Excluir, Recarregar
- [ ] Implementar listbox com load_all_exams()
- [ ] Implementar status label
- [ ] Implementar _on_select_exam_registry()
- [ ] Implementar _carregar_exames_registry()
- [ ] Testar listbox carrega exames

### âœ… ETAPA 4: FormulÃ¡rio Multi-Aba (3h)

- [ ] Criar classe ExamFormDialog (~400 linhas)
- [ ] Implementar _build_tab_basico() (6 campos)
- [ ] Implementar _build_tab_alvos() (2 campos)
- [ ] Implementar _build_tab_faixas() (5 campos)
- [ ] Implementar _build_tab_rp() (1 campo)
- [ ] Implementar _build_tab_export() (2 campos)
- [ ] Implementar _build_tab_controles() (2 campos)
- [ ] Implementar _collect_form_data()
- [ ] Implementar _salvar()
- [ ] Testar abas carregam dados

### âœ… ETAPA 5: IntegraÃ§Ã£o JSON (2h)

- [ ] Implementar _on_exame_salvo() callback
- [ ] Testar save JSON em config/exams/
- [ ] Testar registry.load() recarrega
- [ ] Testar listbox atualiza apÃ³s save
- [ ] Testar recarregar registry button
- [ ] Testar fluxo completo: Novo â†’ Form â†’ Save â†’ Registry â†’ UI

### âœ… ETAPA 6: Testes & Polimento (1-2h)

- [ ] Criar tests/test_fase5_registry_editor.py
- [ ] Implementar 5+ casos de teste
- [ ] Executar pytest
- [ ] Teste manual: Novo exame
- [ ] Teste manual: Editar exame
- [ ] Teste manual: Excluir exame
- [ ] Teste manual: ValidaÃ§Ã£o
- [ ] Polir UI (tooltips, cores, msgs)
- [ ] Atualizar TODO.md e LEITURA_5MIN.md

---

## ğŸ�¯ SUCESSO = Quando?

**Fase 5 Completa quando:**

1. âœ… Aba "Exames (Registry)" funciona
2. âœ… Listbox mostra todos exames do registry
3. âœ… "Novo Exame" abre formulÃ¡rio multi-aba
4. âœ… FormulÃ¡rio salva JSON em `config/exams/<slug>.json`
5. âœ… Registry recarrega apÃ³s save
6. âœ… Exame novo aparece no listbox
7. âœ… "Editar" preenche formulÃ¡rio com dados existentes
8. âœ… "Excluir" remove arquivo JSON
9. âœ… ValidaÃ§Ã£o rejeita dados invÃ¡lidos
10. âœ… Todos testes passam (pytest)
11. âœ… UI polida e funcional
12. âœ… DocumentaÃ§Ã£o atualizada (TODO.md, LEITURA_5MIN.md)

---

## ğŸ“� CHECKLIST FINAL

Antes de marcar Fase 5 como **COMPLETA**:

```
IMPLEMENTAÃ‡ÃƒO
- [ ] RegistryExamEditor class criada
- [ ] ExamFormDialog class criada
- [ ] 6 abas formulÃ¡rio implementadas
- [ ] JSON save implementado
- [ ] Registry reload integrado
- [ ] Aba "Exames (Registry)" adicionada
- [ ] Todos callbacks implementados

TESTES
- [ ] Pytest cases passam
- [ ] Teste manual: Novo exame
- [ ] Teste manual: Editar exame
- [ ] Teste manual: Excluir exame
- [ ] Teste manual: Recarregar registry
- [ ] ValidaÃ§Ã£o de schema funciona

POLIMENTO
- [ ] UI sem erros visuais
- [ ] Mensagens claras
- [ ] Error handling robusto
- [ ] DocumentaÃ§Ã£o atualizada
- [ ] Menu button "Incluir Novo Exame" funciona

DOCUMENTAÃ‡ÃƒO
- [ ] TODO.md marcado Fase 5 = FEITO
- [ ] LEITURA_5MIN.md status = 100%
- [ ] CÃ³digo comentado
- [ ] Docstrings completas
```

---

**PrÃ³ximo Passo:** Iniciar ETAPA 1 â€” PreparaÃ§Ã£o & Design

**Tempo Total Estimado:** 11-12 horas (dividir em 2-3 dias)

**Prioridade:** ğŸ”´ **ALTA** â€” Bloqueante para UI gerenciÃ¡vel

