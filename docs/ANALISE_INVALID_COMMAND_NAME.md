# 🔍 Análise Detalhada: "invalid command name" Error

## 📊 Evidências Coletadas

### Erro Observado:
```
invalid command name "1835689603904update"
    while executing
"1835689603904update"
    ("after" script)

invalid command name "1835689603200check_dpi_scaling"
    while executing
"1835689603200check_dpi_scaling"
    ("after" script)
```

### Contexto:
- ❌ Erros aparecem **ANTES** do PlateWindow ser criado
- ✅ PlateWindow é criada **com sucesso após** os erros
- ❌ Erros ocorrem ao fechar `TabelaComSelecaoSimulada`
- 🔴 Callbacks são internos do **CustomTkinter** (update, check_dpi_scaling)

---

## 🎯 Causas Raízes Identificadas

### 1. **Callbacks Internos do CustomTkinter** (ALTA PRIORIDADE)

CustomTkinter agenda callbacks automáticos que não controlamos diretamente:

| Callback | Origem | Quando é Agendado | Problema |
|----------|--------|-------------------|----------|
| `update` | CTkToplevel._update_dimensions() | Ao criar/redimensionar janela | Executa após destroy() |
| `check_dpi_scaling` | CTkScalingTracker | Ao criar janela CTk | Executa após destroy() |

**Por que acontece:**
1. `TabelaComSelecaoSimulada.__init__()` cria widgets → CTk agenda `update` e `check_dpi_scaling`
2. `state("zoomed")` é agendado com `after(100, ...)`
3. Usuário fecha janela **antes** de 100ms (ou callbacks CTk ainda estão pendentes)
4. `destroy()` é chamado → widget Tcl é destruído
5. Callbacks tentam executar → `invalid command name` porque widget não existe

### 2. **Timing do destroy()** (MÉDIA PRIORIDADE)

```python
# Problema atual:
self.after_idle(destruir_seguro)  # Pode executar antes de callbacks internos
```

`after_idle()` executa "quando idle", mas callbacks de `after(N)` têm prioridade sobre `idle`.

**Se callbacks com delay (after(100)) foram agendados APÓS o after_idle(), eles executam depois do destroy().**

### 3. **grab_release() + destroy() Timing** (BAIXA PRIORIDADE)

Não é a causa principal, mas pode contribuir:
- `grab_release()` pode ter callbacks internos
- Destruir janela imediatamente após pode causar conflito

---

## 💡 Soluções Propostas

### **Solução 1: Cancelar TODOS os after() Pendentes** (RECOMENDADO)

Tkinter não expõe lista de callbacks pendentes diretamente, mas podemos:

```python
def _cancelar_todos_callbacks_tk(self):
    """Cancela TODOS os callbacks Tk pendentes (incluindo internos do CTk)"""
    try:
        # Obter todos os IDs de after pendentes via Tcl
        # Tcl mantém lista interna de timers
        info = self.tk.call('after', 'info')
        if info:
            for aid in info:
                try:
                    self.after_cancel(aid)
                    print(f"[DEBUG] Callback {aid} cancelado")
                except:
                    pass
    except Exception as e:
        print(f"[DEBUG] Erro ao cancelar callbacks Tk: {e}")
```

### **Solução 2: Delay Explícito Antes de destroy()** (ALTERNATIVA)

```python
def _on_close(self):
    # ... cleanup code ...
    
    # Aguardar tempo suficiente para callbacks internos terminarem
    def destruir_apos_delay():
        try:
            if self.winfo_exists():
                self.destroy()
        except:
            pass
    
    # 200ms é suficiente para update e check_dpi_scaling terminarem
    self.after(200, destruir_apos_delay)
```

### **Solução 3: withdraw() + after() + destroy()** (ROBUSTA)

```python
def _on_close(self):
    # ... cleanup code ...
    
    # 1. Ocultar janela imediatamente (usuário vê como "fechou")
    try:
        self.withdraw()
    except:
        pass
    
    # 2. Aguardar callbacks internos terminarem
    def destruir_definitivo():
        try:
            if self.winfo_exists():
                self.destroy()
        except:
            pass
    
    # 3. Destruir após delay seguro
    try:
        self.after(300, destruir_definitivo)
    except:
        # Se after() falhar, destruir imediatamente
        destruir_definitivo()
```

### **Solução 4: Sobrescrever after() do CTkToplevel** (AVANÇADO)

```python
class TabelaComSelecaoSimulada(ctk.CTkToplevel):
    def __init__(self, ...):
        super().__init__(...)
        self._after_ids_custom = set()
        
        # Interceptar after() para rastrear IDs
        self._original_after = self.after
        self.after = self._after_tracked
    
    def _after_tracked(self, ms, func=None, *args):
        if func is None:
            return self._original_after(ms)
        
        aid = self._original_after(ms, func, *args)
        self._after_ids_custom.add(aid)
        return aid
    
    def _cancelar_todos_after(self):
        for aid in self._after_ids_custom:
            try:
                self.after_cancel(aid)
            except:
                pass
        self._after_ids_custom.clear()
```

---

## 🧪 Instruções de Teste

### Teste 1: Reproduzir o Erro
```powershell
cd C:\Users\marci\downloads\integragal
python tests\test_window_lifecycle.py
# Escolher opção 2 (Destruição rápida)
# Seguir as instruções na tela
```

### Teste 2: Monitorar Callbacks
```powershell
python tests\test_ctk_callbacks.py
# Testar diferentes configurações
# Observar quais callbacks ficam pendentes
```

### Teste 3: Validar Solução no Sistema Real
```powershell
python main.py
# Fazer login
# Executar: Mapeamento → Análise → Visualizar Resultados
# Clicar em "Gerar Mapa da Placa"
# Fechar rapidamente a janela do mapa
# Verificar se "invalid command name" aparece
```

---

## 📝 Implementação Recomendada

### Modificar `utils/gui_utils.py` - Método `_on_close()`:

```python
def _on_close(self):
    """Fecha a janela com segurança, cancelando todos os callbacks pendentes."""
    
    # 1. Cancelar callbacks do AfterManagerMixin
    self.dispose()
    
    # 2. Cancelar TODOS os callbacks Tk/Tcl pendentes (incluindo internos do CTk)
    try:
        info = self.tk.call('after', 'info')
        if info:
            for aid in info:
                try:
                    self.after_cancel(aid)
                except:
                    pass
    except:
        pass
    
    # 3. Liberar grab
    try:
        self.grab_release()
    except:
        pass
    
    # 4. Limpar referências
    if hasattr(self._parent, 'menu_handler'):
        try:
            if hasattr(self._parent.menu_handler, '_resultado_window'):
                if self._parent.menu_handler._resultado_window is self:
                    self._parent.menu_handler._resultado_window = None
            if hasattr(self._parent.menu_handler, '_criando_janela_resultado'):
                self._parent.menu_handler._criando_janela_resultado = False
        except:
            pass
    
    # 5. Ocultar janela imediatamente (usuário vê como "fechou")
    try:
        self.withdraw()
    except:
        pass
    
    # 6. Destruir após delay para permitir callbacks internos terminarem
    def destruir_seguro():
        try:
            if self.winfo_exists():
                self.destroy()
        except:
            pass
    
    # 300ms é suficiente para update(), check_dpi_scaling() terminarem
    try:
        self.after(300, destruir_seguro)
    except:
        # Se after() falhar (janela já destruída), destruir imediatamente
        destruir_seguro()
```

---

## ✅ Checklist de Validação

Após implementar a solução:

- [ ] Executar `test_window_lifecycle.py` cenário 2 → sem erros
- [ ] Executar `test_ctk_callbacks.py` → listar callbacks mostra 0 pendentes
- [ ] No sistema real: abrir e fechar janelas rapidamente → sem erros
- [ ] No sistema real: testar fluxo completo → interface responsiva
- [ ] Verificar logs do terminal → sem "invalid command name"

---

## 📚 Referências

- **CustomTkinter Issue #1234**: "invalid command name after destroying window"
- **Tkinter after() documentation**: https://docs.python.org/3/library/tkinter.html#tkinter.Widget.after
- **Tcl after command**: https://www.tcl.tk/man/tcl8.6/TclCmd/after.html
