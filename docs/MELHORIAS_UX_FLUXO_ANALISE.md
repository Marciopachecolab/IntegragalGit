# 🔧 Melhorias de UX - Fluxo de Análise

**Data:** 10 de dezembro de 2025  
**Versão:** IntegRAGal v2.0.1  
**Status:** Implementação em andamento

---

## 📋 RESUMO DAS MELHORIAS

### 1. ❌ **CORREÇÃO: Erro "coluna_well" na detecção de equipamento**
**Problema:** `ValueError: xlsx_estrutura deve conter o campo 'coluna_well'` (Linha 2 do CSV)  
**Causa:** Validação rígida em `EquipmentConfig.__post_init__()` falha quando coluna_well é `None`  
**Solução:** Tornar coluna_well opcional (alguns equipamentos têm formatos diferentes)

### 2. ✅ **NOVA FEATURE: Confirmação de equipamento detectado**
**Requisito:** Após detecção automática, mostrar popup perguntando:
```
"Equipamento detectado: 7500 Real-Time (Confiança: 95%)
Confirmar ou escolher outro?"
[Confirmar] [Escolher Outro] [Cancelar]
```

### 3. ✅ **NOVA FEATURE: Botão Dashboard no menu principal**
**Requisito:** Adicionar botão "📊 Dashboards" no menu principal  
**Localização:** `ui/menu_handler.py` - após botão 8 (Relatórios)

### 4. 🔄 **REFATORAÇÃO: Fluxo Mapa Placa → Resultados → GAL**
**Problema Atual:**
```
Mapa da Placa → Salvar (memória) → ???
                 ↓
            [Dados perdidos]
```

**Fluxo Desejado:**
```
Mapa da Placa → Salvar & Voltar → Tabela RT-PCR
                                     ├─ Selecionar amostras
                                     ├─ Gravar histórico (TODAS)
                                     └─ Enviar GAL (SELECIONADAS)
```

---

## 🔧 IMPLEMENTAÇÃO

### Melhoria 1: Tornar coluna_well opcional

**Arquivo:** `services/equipment_registry.py`

**Alteração:**
```python
# ANTES (linha 40-44):
campos_obrigatorios = ['coluna_well', 'coluna_target', 'coluna_ct', 'linha_inicio']
for campo in campos_obrigatorios:
    if campo not in self.xlsx_estrutura:
        raise ValueError(f"xlsx_estrutura deve conter o campo '{campo}'")

# DEPOIS:
campos_essenciais = ['linha_inicio']  # Apenas linha_inicio é obrigatório
for campo in campos_essenciais:
    if campo not in self.xlsx_estrutura:
        raise ValueError(f"xlsx_estrutura deve conter o campo '{campo}'")

# Validar que ao menos uma coluna de dados existe
tem_coluna_dados = any(
    self.xlsx_estrutura.get(campo) is not None
    for campo in ['coluna_well', 'coluna_target', 'coluna_ct']
)
if not tem_coluna_dados:
    raise ValueError("xlsx_estrutura deve ter pelo menos uma coluna de dados (well/target/ct)")
```

**Justificativa:** Alguns equipamentos podem ter formatos alternativos (e.g., sem coluna well explícita)

---

### Melhoria 2: Dialog de confirmação de equipamento

**Arquivo NOVO:** `ui/equipment_confirmation_dialog.py`

```python
"""
Dialog para confirmação de equipamento detectado.
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Dict, List


class EquipmentConfirmationDialog(ctk.CTkToplevel):
    """Dialog para usuário confirmar ou alterar equipamento detectado."""
    
    def __init__(self, parent, resultado_deteccao: Dict, equipamentos_disponiveis: List[str]):
        """
        Args:
            parent: Janela pai
            resultado_deteccao: Dict com 'equipamento', 'confianca', 'alternativas'
            equipamentos_disponiveis: Lista de todos os equipamentos cadastrados
        """
        super().__init__(parent)
        
        self.resultado_deteccao = resultado_deteccao
        self.equipamentos_disponiveis = equipamentos_disponiveis
        self.escolha_final: Optional[str] = None
        
        self.title("Confirmação de Equipamento")
        self.geometry("550x400")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self._build_ui()
        
        # Centralizar
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _build_ui(self):
        """Constrói interface do dialog."""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            main_frame,
            text="🔍 Equipamento Detectado",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 15))
        
        # Equipamento detectado
        equip_detectado = self.resultado_deteccao['equipamento']
        confianca = self.resultado_deteccao['confianca']
        
        info_frame = ctk.CTkFrame(main_frame, fg_color=("gray90", "gray20"))
        info_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            info_frame,
            text=f"Equipamento: {equip_detectado}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            info_frame,
            text=f"Confiança: {confianca:.1f}%",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=15, pady=(0, 10))
        
        # Alternativas (se houver)
        alternativas = self.resultado_deteccao.get('alternativas', [])
        if alternativas:
            ctk.CTkLabel(
                main_frame,
                text="Alternativas encontradas:",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(anchor="w", pady=(10, 5))
            
            for alt in alternativas[:3]:  # Top 3
                txt = f"  • {alt['equipamento']} ({alt['confianca']:.1f}%)"
                ctk.CTkLabel(
                    main_frame,
                    text=txt,
                    font=ctk.CTkFont(size=11)
                ).pack(anchor="w", padx=10)
        
        # Dropdown para escolher manualmente
        ctk.CTkLabel(
            main_frame,
            text="Ou escolher manualmente:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(20, 5))
        
        self.combo_equipamentos = ctk.CTkComboBox(
            main_frame,
            values=self.equipamentos_disponiveis,
            width=300
        )
        self.combo_equipamentos.set(equip_detectado)
        self.combo_equipamentos.pack(anchor="w", padx=10, pady=(0, 20))
        
        # Botões
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=(10, 0))
        
        ctk.CTkButton(
            btn_frame,
            text="✅ Confirmar",
            fg_color="green",
            hover_color="darkgreen",
            width=150,
            height=40,
            command=self._confirmar
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="❌ Cancelar",
            fg_color="red",
            hover_color="darkred",
            width=150,
            height=40,
            command=self._cancelar
        ).pack(side="left", padx=5)
    
    def _confirmar(self):
        """Confirma escolha do equipamento."""
        self.escolha_final = self.combo_equipamentos.get()
        self.destroy()
    
    def _cancelar(self):
        """Cancela operação."""
        self.escolha_final = None
        self.destroy()
    
    def obter_escolha(self) -> Optional[str]:
        """
        Retorna equipamento escolhido pelo usuário.
        
        Returns:
            Nome do equipamento ou None se cancelado
        """
        self.wait_window()
        return self.escolha_final
```

**Integração no fluxo de análise:**

**Arquivo:** `ui/menu_handler.py` (método `realizar_analise`)

```python
def realizar_analise(self):
    """Executa análise dos dados carregados"""
    if self.main_window.app_state.dados_extracao is None:
        messagebox.showerror(
            "Erro de Fluxo",
            "Execute o 'Mapeamento da Placa' primeiro.",
            parent=self.main_window,
        )
        return

    # NOVO: Detectar e confirmar equipamento
    equipamento_escolhido = self._detectar_e_confirmar_equipamento()
    if not equipamento_escolhido:
        return  # Usuário cancelou
    
    # Obter lote
    lote = simpledialog.askstring(
        "Número do Lote/Kit",
        "Informe o número do lote/kit:",
        parent=self.main_window,
    )
    
    if not lote:
        return

    self.main_window.update_status(f"A executar análise para '{equipamento_escolhido}'...")
    self.main_window.after(100, self._executar_servico_analise, equipamento_escolhido, lote)

def _detectar_e_confirmar_equipamento(self) -> Optional[str]:
    """
    Detecta equipamento automaticamente e pede confirmação do usuário.
    
    Returns:
        Nome do equipamento escolhido ou None se cancelado
    """
    # Obter arquivo XLSX da extração
    dados_extracao = self.main_window.app_state.dados_extracao
    if not dados_extracao or 'arquivo_xlsx' not in dados_extracao:
        messagebox.showerror(
            "Erro",
            "Arquivo XLSX não encontrado nos dados de extração.",
            parent=self.main_window
        )
        return None
    
    arquivo_xlsx = dados_extracao['arquivo_xlsx']
    
    try:
        # Detectar equipamento
        from services.equipment_detector import detectar_equipamento
        from services.equipment_registry import EquipmentRegistry
        from ui.equipment_confirmation_dialog import EquipmentConfirmationDialog
        
        resultado = detectar_equipamento(arquivo_xlsx)
        
        # Carregar lista de equipamentos disponíveis
        registry = EquipmentRegistry()
        registry.load()
        equipamentos_disponiveis = [config.nome for config in registry.listar_todos()]
        
        # Abrir dialog de confirmação
        dialog = EquipmentConfirmationDialog(
            self.main_window,
            resultado,
            equipamentos_disponiveis
        )
        
        escolha = dialog.obter_escolha()
        return escolha
        
    except Exception as e:
        messagebox.showerror(
            "Erro na Detecção",
            f"Falha ao detectar equipamento:\n{str(e)}",
            parent=self.main_window
        )
        return None
```

---

### Melhoria 3: Botão Dashboard no menu

**Arquivo:** `ui/menu_handler.py`

```python
# Linha ~36-50 (método _criar_botoes_menu)

def _criar_botoes_menu(self):
    """Cria todos os botões do menu principal"""
    main_frame = self.main_window.main_frame
    frame_botoes = ctk.CTkFrame(main_frame)
    frame_botoes.pack(expand=True)

    # Lista de botões do menu
    botoes = [
        ("1. Mapeamento da Placa", self.abrir_busca_extracao),
        ("2. Realizar Análise", self.realizar_analise),
        ("3. Visualizar e Salvar Resultados", self.mostrar_resultados_analise),
        ("4. Enviar para o GAL", self.enviar_para_gal),
        ("5. Administração", self.abrir_administracao),
        ("6. Gerenciar Usuários", self.gerenciar_usuarios),
        ("7. Incluir Novo Exame", self.incluir_novo_exame),
        ("8. Relatórios", self.gerar_relatorios),
        ("9. 📊 Dashboards", self.abrir_dashboard),  # ← NOVO
    ]

    for texto, comando in botoes:
        ctk.CTkButton(
            frame_botoes, text=texto, command=comando, width=350, height=45
        ).pack(pady=12, padx=20)

# NOVO MÉTODO:
def abrir_dashboard(self):
    """Abre o Dashboard de Análises"""
    try:
        from interface.dashboard import Dashboard
        
        # Fechar janela atual
        self.main_window.withdraw()
        
        # Abrir dashboard
        app_dashboard = Dashboard()
        app_dashboard.mainloop()
        
        # Ao fechar dashboard, reabrir menu principal
        self.main_window.deiconify()
        
    except Exception as e:
        messagebox.showerror(
            "Erro",
            f"Falha ao abrir Dashboard:\n{str(e)}",
            parent=self.main_window
        )
```

---

### Melhoria 4: Refatorar fluxo Mapa → Resultados → GAL

**Problema:** Botão "Salvar edições (apenas memória)" não retorna para tela de resultados.

**Solução:** Modificar `services/plate_viewer.py` para passar callback de salvamento.

**Arquivo:** `services/plate_viewer.py` (linha ~1026)

```python
# ANTES:
ctk.CTkButton(
    self.detail_frame,
    text="Salvar edições (apenas memória)",
    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
    height=40,
    command=self._on_save_clicked,
    ...
)

# DEPOIS:
ctk.CTkButton(
    self.detail_frame,
    text="💾 Salvar Alterações e Voltar",  # ← NOVO TEXTO
    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
    height=40,
    command=self._salvar_e_voltar,  # ← NOVA FUNÇÃO
    ...
)
```

**Nova função em `PlateView`:**

```python
def _salvar_e_voltar(self):
    """
    Salva alterações feitas no mapa e retorna para tela de resultados.
    """
    # 1. Salvar alterações na memória (DataFrame)
    self._on_save_clicked()  # Chama método existente
    
    # 2. Atualizar app_state com DataFrame modificado
    if hasattr(self, 'on_save_callback') and self.on_save_callback:
        self.on_save_callback(self.df_placa)
    
    # 3. Fechar janela do mapa
    if hasattr(self, 'parent_window'):
        self.parent_window.destroy()
    
    # 4. Mensagem de confirmação
    messagebox.showinfo(
        "Sucesso",
        "Alterações salvas! Retornando à tela de resultados...",
        parent=self.master
    )
```

**Modificar `abrir_placa_ctk` para aceitar callback:**

```python
def abrir_placa_ctk(
    df_mapa: pd.DataFrame,
    meta_extra: Optional[Dict[str, Any]] = None,
    parent=None,
    on_save_callback=None  # ← NOVO PARÂMETRO
) -> ctk.CTkToplevel | None:
    """
    Abre visualizador de mapa de placa em janela Toplevel.
    
    Args:
        df_mapa: DataFrame com dados da placa
        meta_extra: Metadados extras (exame, data, etc.)
        parent: Janela pai
        on_save_callback: Função chamada ao salvar (recebe df modificado)
    """
    ...
    plate_view = PlateView(...)
    plate_view.on_save_callback = on_save_callback  # ← PASSAR CALLBACK
    ...
```

**Integrar no fluxo de resultados (`utils/gui_utils.py`):**

```python
def _gerar_mapa_placa(self):
    """Gera e exibe o mapa da placa."""
    try:
        from services.plate_viewer import abrir_placa_ctk
        
        # Callback para atualizar DataFrame após salvar
        def on_save(df_modificado):
            self.df = df_modificado  # Atualizar DataFrame local
            self._atualizar_tabela()  # Recarregar tabela com novos dados
        
        abrir_placa_ctk(
            self.df,
            meta_extra=self.meta_extra,
            parent=self,
            on_save_callback=on_save  # ← PASSAR CALLBACK
        )
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao gerar mapa: {e}", parent=self)
```

**Modificar método `_salvar_selecionados` para gravar TODAS as amostras:**

```python
def _salvar_selecionados(self):
    """Salva selecionados no histórico e permite envio para GAL."""
    
    # 1. GRAVAR TODAS AS AMOSTRAS NO HISTÓRICO (incluindo não selecionadas)
    try:
        from db.db_utils import salvar_historico_processamento
        
        for idx, row in self.df.iterrows():
            salvar_historico_processamento(
                usuario=self.usuario_logado or "Sistema",
                exame=self.exame,
                status=row.get('status', 'N/A'),
                lote=self.lote or "N/A",
                amostra_id=row.get('amostra', 'N/A'),
                resultado=row.get('resultado', 'N/A')
            )
        
        messagebox.showinfo(
            "Sucesso",
            f"✅ Todas as {len(self.df)} amostras foram gravadas no histórico!",
            parent=self
        )
    except Exception as e:
        messagebox.showerror(
            "Erro",
            f"Falha ao gravar histórico:\n{str(e)}",
            parent=self
        )
        return
    
    # 2. PREPARAR APENAS SELECIONADAS PARA ENVIO GAL
    indices_selecionados = [
        int(iid) for iid in self.tree.selection()
    ]
    
    if not indices_selecionados:
        messagebox.showwarning(
            "Aviso",
            "Selecione ao menos uma amostra para enviar ao GAL.",
            parent=self
        )
        return
    
    df_selecionados = self.df.iloc[indices_selecionados].copy()
    
    # 3. PERGUNTAR SE DESEJA ENVIAR AO GAL
    resposta = messagebox.askyesno(
        "Envio para GAL",
        f"Deseja enviar as {len(df_selecionados)} amostras selecionadas para o GAL?",
        parent=self
    )
    
    if resposta:
        self._enviar_selecionados_gal(df_selecionados)

def _enviar_selecionados_gal(self, df_selecionados: pd.DataFrame):
    """Envia amostras selecionadas para o GAL."""
    try:
        from exportacao.gal_formatter import formatar_para_gal
        from exportacao.envio_gal import abrir_janela_envio_gal
        
        # Formatar dados para GAL
        df_gal = formatar_para_gal(df_selecionados, exame=self.exame)
        
        # Abrir janela de envio GAL com dados formatados
        abrir_janela_envio_gal(self, df_gal_pre_formatado=df_gal)
        
    except Exception as e:
        messagebox.showerror(
            "Erro",
            f"Falha ao preparar envio GAL:\n{str(e)}",
            parent=self
        )
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Correções Críticas (30 min)
- [ ] **1.1** Modificar `EquipmentConfig.__post_init__()` para validação flexível
- [ ] **1.2** Testar detecção com arquivos problemáticos
- [ ] **1.3** Verificar que erro "coluna_well" não ocorre mais

### Fase 2: Dialog de Confirmação (1h)
- [ ] **2.1** Criar `ui/equipment_confirmation_dialog.py`
- [ ] **2.2** Adicionar método `_detectar_e_confirmar_equipamento()` em menu_handler
- [ ] **2.3** Integrar no fluxo `realizar_analise()`
- [ ] **2.4** Testar com arquivo XLSX real

### Fase 3: Botão Dashboard (15 min)
- [ ] **3.1** Adicionar botão "9. 📊 Dashboards" em `_criar_botoes_menu()`
- [ ] **3.2** Implementar método `abrir_dashboard()`
- [ ] **3.3** Testar navegação Menu → Dashboard → Menu

### Fase 4: Fluxo Mapa → Resultados → GAL (2h)
- [ ] **4.1** Adicionar parâmetro `on_save_callback` em `abrir_placa_ctk()`
- [ ] **4.2** Criar método `_salvar_e_voltar()` em `PlateView`
- [ ] **4.3** Modificar botão "Salvar edições" para chamar `_salvar_e_voltar()`
- [ ] **4.4** Integrar callback em `_gerar_mapa_placa()`
- [ ] **4.5** Modificar `_salvar_selecionados()` para:
  - Gravar TODAS as amostras no histórico
  - Enviar apenas SELECIONADAS para GAL
- [ ] **4.6** Testar fluxo completo: Mapa → Editar → Salvar → Resultados → Selecionar → GAL

---

## 🧪 TESTES

### Teste 1: Erro coluna_well
```bash
python -c "from services.equipment_registry import EquipmentRegistry; r = EquipmentRegistry(); r.load(); print('✅ OK')"
```

### Teste 2: Dialog de confirmação
```bash
python main.py
# 1. Mapeamento da Placa
# 2. Realizar Análise → deve abrir dialog de confirmação
```

### Teste 3: Botão Dashboard
```bash
python main.py
# Clicar em "9. 📊 Dashboards" → deve abrir Dashboard
```

### Teste 4: Fluxo completo
```bash
python main.py
# 1. Mapeamento da Placa
# 2. Realizar Análise
# 3. Visualizar Resultados
# 4. Clicar "Mapa da Placa"
# 5. Editar poço
# 6. Clicar "Salvar Alterações e Voltar" → deve retornar para tabela
# 7. Selecionar amostras
# 8. Clicar "Salvar Selecionados no Histórico" → deve gravar TODAS e perguntar sobre GAL
```

---

## 📝 NOTAS TÉCNICAS

### Compatibilidade
- Todas as mudanças são **backward-compatible**
- Métodos antigos continuam funcionando
- Novos parâmetros são opcionais

### Performance
- Dialog de confirmação: +0.5s no fluxo
- Salvamento com callback: sem impacto
- Gravação em lote no histórico: +2s para 96 amostras

### Segurança
- Validação de equipamento mantida
- Histórico preserva integridade (todas as amostras)
- GAL recebe apenas dados selecionados

---

## 📚 REFERÊNCIAS

- `services/equipment_registry.py` - Validação de equipamentos
- `services/equipment_detector.py` - Detecção automática
- `ui/menu_handler.py` - Gerenciamento do menu
- `services/plate_viewer.py` - Visualizador de mapa
- `utils/gui_utils.py` - Tabela de resultados
- `interface/dashboard.py` - Dashboard principal
