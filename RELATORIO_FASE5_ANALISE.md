# ğŸ“‹ RELATÃ“RIO DE ANÃ�LISE â€” FASE 5 (UI de Cadastro/EdiÃ§Ã£o)

**Data:** 2025-12-07  
**Status Geral:** âš ï¸� **PARCIALMENTE IMPLEMENTADO â€” Requer IntegraÃ§Ã£o com Registry**

---

## 1. SITUAÃ‡ÃƒO ATUAL

### 1.1 Arquivo Existente

**âœ… Implementado:** `services/cadastros_diversos.py` (905 linhas)
- MÃ³dulo unificado para manutenÃ§Ã£o de **4 entidades CSV:**
  - Exames (`banco/exames_config.csv`)
  - Equipamentos (`banco/equipamentos.csv`)
  - Placas (`banco/placas.csv`)
  - Regras (`banco/regras.csv`)

### 1.2 IntegraÃ§Ã£o no Menu

**âœ… Menu Principal:**
- BotÃ£o: **"â€šÃ»Ã¯ Incluir Novo Exame"** (services/menu_handler.py, linha 46)
- AÃ§Ã£o: `self.incluir_novo_exame()` (linha 323)
- Chama: `from ui.cadastros_diversos import CadastrosDiversosWindow` (linha 325)

**â�Œ Problema Identificado:**
- Menu tenta importar de `ui.cadastros_diversos` (linha 325)
- Arquivo real estÃ¡ em `services/cadastros_diversos.py`
- **Import path incorreto â†’ causarÃ¡ erro em runtime**

### 1.3 Arquitetura Implementada

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�
â”‚  CadastrosDiversosWindow (Tkinter Toplevel)         â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ â€¢ Janela com 4 abas (Exames, Equipamentos,          â”‚
â”‚   Placas, Regras)                                   â”‚
â”‚ â€¢ Tabelas ttk.Treeview para cada tipo               â”‚
â”‚ â€¢ FormulÃ¡rios CTkEntry para ediÃ§Ã£o                  â”‚
â”‚ â€¢ BotÃµes: Novo, Salvar, Excluir, Recarregar        â”‚
â”‚                                                     â”‚
â”‚ MÃ©todos por aba:                                    â”‚
â”‚ â€¢ _build_tab_exames()                               â”‚
â”‚ â€¢ _build_tab_equipamentos()                         â”‚
â”‚ â€¢ _build_tab_placas()                               â”‚
â”‚ â€¢ _build_tab_regras()                               â”‚
â”‚                                                     â”‚
â”‚ UtilitÃ¡rios:                                        â”‚
â”‚ â€¢ _load_csv(key)  â†’ lÃª arquivo CSV                  â”‚
â”‚ â€¢ _save_csv(key)  â†’ escreve arquivo CSV             â”‚
â”‚ â€¢ _ensure_csv(key) â†’ cria se nÃ£o existir            â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## 2. ANÃ�LISE DETALHADA DA IMPLEMENTAÃ‡ÃƒO

### 2.1 Aba "Exames" â€” Campos

**âœ… FormulÃ¡rio implementado com campos:**
1. **Nome do exame** (entry_exame)
2. **MÃ³dulo de anÃ¡lise** (entry_modulo)
3. **Tipo de placa** (entry_tipo_placa)
4. **NÃºmero/ID do kit** (entry_numero_kit)
5. **Equipamento associado** (entry_equipamento_exame)

**OperaÃ§Ãµes:**
- Carregar lista de exames (treeview) â€” âœ…
- Selecionar exame â†’ preench formulÃ¡rio â€” âœ…
- Novo exame â†’ limpar formulÃ¡rio â€” âœ…
- Salvar exame â†’ atualizar CSV â€” âœ…
- Excluir exame â†’ remover de CSV â€” âœ…

**Exemplo de fluxo:**
```
UsuÃ¡rio clica "Novo Exame"
  â†’ current_exam_id = None
  â†’ formulÃ¡rio fica vazio

UsuÃ¡rio preenche:
  exame = "VR1e2 Biomanguinhos 7500"
  modulo_analise = "analise.vr1e2_biomanguinhos_7500.analisar_placa_vr1e2_7500"
  tipo_placa = "48"
  numero_kit = "1140"
  equipamento = "7500 Real-Time"

UsuÃ¡rio clica "Salvar"
  â†’ dados adicionados Ã  lista exames_config.csv
  â†’ treeview recarregado
```

### 2.2 Outras Abas

**âœ… Aba "Equipamentos"** (4 campos):
- nome, modelo, fabricante, observacoes
- CRUD completo implementado

**âœ… Aba "Placas"** (4 campos):
- nome, tipo, num_pocos, descricao
- CRUD completo implementado

**âœ… Aba "Regras"** (4 campos):
- nome_regra, exame, descricao, parametros
- CRUD completo implementado

### 2.3 PersistÃªncia

**âœ… CSV Read/Write:**
```python
def _load_csv(self, key: str) -> List[Dict[str, str]]:
    # LÃª CSV com encoding UTF-8, retorna list of dicts
    
def _save_csv(self, key: str, rows: List[Dict[str, str]]) -> None:
    # Escreve CSV com headers, encoding UTF-8
```

**âœ… Logging:**
- Cada operaÃ§Ã£o registrada em `services/logger.py`

---

## 3. LACUNAS E DEFICIÃŠNCIAS (â�Œ Status Fase 5)

### 3.1 **NÃƒO Implementado: IntegraÃ§Ã£o com Registry JSON**

**Requisito da Fase 5:**
> Tela "Gerenciar Exames": lista exames carregados; **formulÃ¡rio Novo/Editar com campos do schema**; validar e salvar em **config/exams/<slug>.json**; **recarregar registry**.

**O que falta:**

| Requisito | Status | Detalhe |
|-----------|--------|---------|
| **Aba "Gerenciar Exames" (novo/editar)** | â�Œ | Atual aba "Exames" sÃ³ edita CSV, nÃ£o JSON |
| **FormulÃ¡rio com schema ExamConfig** | â�Œ | FormulÃ¡rio nÃ£o tem campos: alvos, mapa_alvos, faixas_ct, rps, export_fields, panel_tests_id, controles |
| **Salvar em config/exams/<slug>.json** | â�Œ | Salva apenas em banco/exames_config.csv; sem geraÃ§Ã£o de JSON |
| **ValidaÃ§Ã£o de schema** | â�Œ | Sem validaÃ§Ã£o de faixas_ct (detect_max, inconc_min, inconc_max) |
| **Recarregar registry** | â�Œ | Sem integraÃ§Ã£o com `services.exam_registry.registry.load()` |
| **UI para campos JSON** | â�Œ | Sem form fields para alvos/mapa_alvos/export_fields |

### 3.2 **Erro no Menu Handler**

**Problema:**
```python
# services/menu_handler.py, linha 325 (INCORRETO)
from ui.cadastros_diversos import CadastrosDiversosWindow
```

**Realidade:**
- Arquivo estÃ¡ em `services/cadastros_diversos.py`
- Import correto deveria ser: `from services.cadastros_diversos import CadastrosDiversosWindow`

**Impacto:** Menu button "Incluir Novo Exame" falharÃ¡ com `ModuleNotFoundError`

### 3.3 **DuplicaÃ§Ã£o Potencial**

Se menu correto, usuÃ¡rio pode editar **duas fontes:**
1. **CSV** (`banco/exames_config.csv`) â€” via UI atual
2. **JSON** (`config/exams/<slug>.json`) â€” fonte de verdade da Fase 3

**InconsistÃªncia:** UsuÃ¡rio edita exame no CSV, mas registry carrega JSON sobrescrevendo. MudanÃ§as no CSV perdidas.

---

## 4. O QUE A FASE 5 DEVERIA SER

### 4.1 Tela "Gerenciar Exames" Completa

**Layout proposto:**
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�
â”‚  Gerenciar Exames â€” Registry Editor                    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                        â”‚
â”‚  [Novo]  [Editar]  [Excluir]  [Recarregar Registry]  â”‚
â”‚                                                        â”‚
â”‚  Lista de Exames:                                      â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�                      â”‚
â”‚  â”‚ â€¢ VR1e2 Biomanguinhos 7500   â”‚  (selecionado)      â”‚
â”‚  â”‚ â€¢ ZDC Biomanguinhos 7500     â”‚                      â”‚
â”‚  â”‚ â€¢ VR1                        â”‚                      â”‚
â”‚  â”‚ â€¢ VR2                        â”‚                      â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                      â”‚
â”‚                                                        â”‚
â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€  â”‚
â”‚  FORMULÃ�RIO (aba selecionada)                          â”‚
â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€  â”‚
â”‚                                                        â”‚
â”‚  [BÃ¡sico] [Alvos] [Faixas CT] [RP] [Export] [Controles]â”‚
â”‚                                                        â”‚
â”‚  â”Œâ”€ BÃ¡sico â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�         â”‚
â”‚  â”‚ Nome Exame:          [____________]      â”‚         â”‚
â”‚  â”‚ Slug:                [____________]      â”‚         â”‚
â”‚  â”‚ Equipamento:         [____________]      â”‚         â”‚
â”‚  â”‚ Tipo Placa:          [48 â–¼]              â”‚         â”‚
â”‚  â”‚ Esquema Agrupamento: [96->48 â–¼]          â”‚         â”‚
â”‚  â”‚ Kit CÃ³digo:          [____________]      â”‚         â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜         â”‚
â”‚                                                        â”‚
â”‚                [Salvar]  [Cancelar]                    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 4.2 Multi-Aba para Schema ExamConfig

**Aba "Alvos":**
```
Alvos (separados por ;):
[SC2; HMPV; INF A; INF B; ADV; RSV; HRV]

Mapa de Alvos (alias â†’ canonical):
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�
â”‚ SC2  â†’ SC2              â”‚
â”‚ INFA â†’ INF A            â”‚
â”‚ SARS-COV-2 â†’ SC2        â”‚
â”‚ ADV  â†’ ADV              â”‚
â”‚ ADENOVIRUS â†’ ADV        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
[+] [âˆ’] Novo Alias
```

**Aba "Faixas CT":**
```
detect_max:    [38.0 ]  â†� CT mÃ¡ximo detectÃ¡vel
inconc_min:    [38.01]  â†� CT mÃ­nimo inconclusivo
inconc_max:    [40.0 ]  â†� CT mÃ¡ximo inconclusivo
rp_min:        [15.0 ]  â†� CT mÃ­nimo referÃªncia positiva
rp_max:        [35.0 ]  â†� CT mÃ¡ximo referÃªncia positiva
```

**Aba "Export Fields":**
```
Analitos a exportar (separados por ;):
[Sars-Cov-2; Influenzaa; influenzab; RSV; adenovÃ­rus; ...]

Panel Tests ID:
[1 ]

Kit CÃ³digo:
[1140 ]
```

**Aba "Controles":**
```
Controles Negativos (CN) â€” poÃ§os:
[G11+G12]

Controles Positivos (CP) â€” poÃ§os:
[H11+H12]
```

### 4.3 Fluxo de Salva Proposto

```
UsuÃ¡rio clica [Salvar]
  â†“
Validar campos:
  â€¢ nome_exame: obrigatÃ³rio
  â€¢ tipo_placa: nÃºmero vÃ¡lido
  â€¢ faixas_ct.detect_max < inconc_min < inconc_max
  â€¢ alvos: lista nÃ£o vazia (se seÃ§Ã£o editada)
  â†“
Gerar slug: "vr1e2_biomanguinhos_7500"
  â†“
Criar ExamConfig object
  â†“
Salvar em: config/exams/{slug}.json (JSON estruturado)
  â†“
Recarregar registry:
  registry.load()  â†� carrega CSV + JSON novo
  â†“
Atualizar listview (refletir novo exame)
  â†“
Mensagem: "Exame salvo com sucesso! âœ“"
```

---

## 5. PLANO DE IMPLEMENTAÃ‡ÃƒO (FASE 5 COMPLETA)

### 5.1 Fixes Imediatos

**1. Corrigir import em menu_handler.py:**
```python
# services/menu_handler.py, linha 325
# DE:
from ui.cadastros_diversos import CadastrosDiversosWindow
# PARA:
from services.cadastros_diversos import CadastrosDiversosWindow
```

**2. Criar alias em ui/__init__.py ou ui/cadastros_diversos.py:**
```python
# ui/cadastros_diversos.py (novo)
from services.cadastros_diversos import CadastrosDiversosWindow

__all__ = ["CadastrosDiversosWindow"]
```

### 5.2 Nova Funcionalidade: Aba "Gerenciar Exames" (Registry)

**Arquivo:** `services/cadastros_diversos.py` â€” adicionar nova aba

**Classe auxiliar:**
```python
@dataclass
class RegistryExamEditor:
    """Gerencia ediÃ§Ã£o de exames via JSON + Registry"""
    
    def load_exam(self, slug: str) -> ExamConfig:
        """Carrega exame do registry"""
        
    def save_exam(self, exam_cfg: ExamConfig) -> None:
        """Salva ExamConfig em config/exams/{slug}.json"""
        
    def validate_exam(self, exam_cfg: ExamConfig) -> Tuple[bool, str]:
        """Valida schema ExamConfig"""
        
    def reload_registry(self) -> None:
        """Recarrega registry apÃ³s salvar"""
```

**UI Components:**
- Listbox com exames carregados do registry
- Multi-aba form (BÃ¡sico, Alvos, Faixas CT, RP, Export, Controles)
- BotÃµes: Novo, Editar, Excluir, Salvar, Cancelar, Recarregar Registry
- ValidaÃ§Ã£o de entrada em tempo real

### 5.3 Cronograma Estimado

| Tarefa | EsforÃ§o | Prioridade |
|--------|---------|-----------|
| Fix import menu_handler | 5 min | ğŸ”´ **CRÃ�TICA** |
| Criar ui/cadastros_diversos.py (alias) | 2 min | ğŸŸ¡ Alta |
| Adicionar classe RegistryExamEditor | 2 horas | ğŸŸ¡ Alta |
| Build UI multi-aba com CTkTabview | 3 horas | ğŸŸ¡ Alta |
| Implementar _build_registry_form() | 2 horas | ğŸŸ¡ Alta |
| Integrar validaÃ§Ã£o de schema | 1 hora | ğŸŸ¡ Alta |
| Testar CRUD JSON + reload registry | 1 hora | ğŸŸ¡ Alta |
| **Total estimado** | **~9-10 horas** | |

---

## 6. CHECKLIST DA FASE 5

### Status Atual (Before):

- [ ] Tela "Gerenciar Exames" lista exames carregados
- [ ] FormulÃ¡rio com campos do schema ExamConfig
- [ ] Novo/Editar exame
- [ ] Validar dados (schema, faixas CT)
- [ ] Salvar em `config/exams/<slug>.json`
- [ ] Recarregar registry automaticamente
- [ ] Mensagens de sucesso/erro

### Implementado Atualmente:

- [x] UI bÃ¡sica com 4 abas (CSV CRUD â€” nÃ£o JSON)
- [x] BotÃµes Novo, Salvar, Excluir, Recarregar
- [x] PersistÃªncia em CSV
- [x] IntegraÃ§Ã£o no menu

### Faltando (Para Completude):

- [ ] IntegraÃ§Ã£o com `exam_registry.py` (**CRÃ�TICA**)
- [ ] Aba "Gerenciar Exames" (registry, nÃ£o CSV)
- [ ] FormulÃ¡rio multi-aba para ExamConfig
- [ ] JSON save/load para `config/exams/`
- [ ] ValidaÃ§Ã£o de faixas_ct
- [ ] Registry reload apÃ³s salvar
- [ ] Tratamento de slug duplicado
- [ ] Tests para CRUD JSON

---

## 7. COMPARAÃ‡ÃƒO: Implementado vs. Requisito

| Requisito Fase 5 | Implementado | Faltando |
|------------------|--------------|----------|
| **Tela "Gerenciar Exames"** | âœ… Parcial (CSV) | â�Œ JSON/Registry |
| **Lista exames carregados** | âœ… Sim (CSV) | âš ï¸� Deveria vir do registry |
| **FormulÃ¡rio com campos schema** | â�Œ NÃ£o | âš ï¸� Precisa de 13 campos + validaÃ§Ã£o |
| **Novo/Editar exame** | âœ… Sim (CSV) | â�Œ JSON nÃ£o |
| **Validar dados** | âš ï¸� MÃ­nimo | â�Œ Schema validation |
| **Salvar em config/exams/<slug>.json** | â�Œ NÃ£o | âš ï¸� Deveria ser JSON, nÃ£o CSV |
| **Recarregar registry** | â�Œ NÃ£o | âš ï¸� Precisaria registry.load() |

---

## 8. RECOMENDAÃ‡Ã•ES

### ğŸ”´ **CrÃ­tico (Fazer Primeiro):**

1. **Fix import path** â€” menu_handler.py linha 325
   ```python
   from services.cadastros_diversos import CadastrosDiversosWindow  # â†� corrigir
   ```

2. **Criar alias em ui/** â€” evitar duplicaÃ§Ã£o
   ```python
   # ui/cadastros_diversos.py (novo arquivo)
   from services.cadastros_diversos import CadastrosDiversosWindow
   ```

### ğŸŸ¡ **Importante (Para completar Fase 5):**

3. **Estender CadastrosDiversosWindow** â€” adicionar aba "Exames (Registry)"
   - Listar exames do registry (`ExamRegistry.exams.keys()`)
   - FormulÃ¡rio multi-aba para ExamConfig
   - Save JSON + reload registry

4. **Criar RegistryExamEditor class** â€” separar lÃ³gica de UI
   - Load/save ExamConfig
   - Validate schema
   - Handle file I/O

### ğŸŸ¢ **Nice-to-have:**

5. Suporte a YAML alÃ©m de JSON
6. ImportaÃ§Ã£o de exames de arquivo (upload ZIP com JSONs)
7. ExportaÃ§Ã£o de configuraÃ§Ã£o (backup)
8. ValidaÃ§Ã£o visual em tempo real

---

## 9. CONCLUSÃƒO

**Fase 5 â€” Status: âš ï¸� PARCIALMENTE IMPLEMENTADO**

âœ… **O que existe:**
- UI funcional com 4 abas (Exames, Equipamentos, Placas, Regras)
- CRUD em CSV
- IntegraÃ§Ã£o no menu principal
- PersistÃªncia e logging

â�Œ **O que falta (essencial para Fase 5 completa):**
- **IntegraÃ§Ã£o com Registry JSON** â€” todo requisito central da Fase 5
- FormulÃ¡rio com campos do schema ExamConfig
- Save em `config/exams/<slug>.json`
- Recarregar registry apÃ³s salvar
- ValidaÃ§Ã£o de schema completa

**AÃ§Ã£o recomendada:**
1. Fix import crÃ­tico (5 min)
2. Criar nova aba "Exames (Registry)" com formulÃ¡rio multi-aba (~9-10 horas)
3. Testar fluxo completo: novo exame â†’ JSON â†’ registry reload

**Prioridade:** Alta â€” Fase 5 Ã© bloqueante para UI gerenciÃ¡vel de exames.

