# ğŸ“‹ RELATÃ“RIO DE ANÃ�LISE — FASE 5 (UI de Cadastro/Edição)



**Data:** 2025-12-07  

**Status Geral:** âš ï¸� **PARCIALMENTE IMPLEMENTADO — Requer Integração com Registry**



---



## 1. SITUAÃ‡ÃƒO ATUAL



### 1.1 Arquivo Existente



**âœ… Implementado:** `services/cadastros_diversos.py` (905 linhas)

- Módulo unificado para manutenção de **4 entidades CSV:**

  - Exames (`banco/exames_config.csv`)

  - Equipamentos (`banco/equipamentos.csv`)

  - Placas (`banco/placas.csv`)

  - Regras (`banco/regras.csv`)



### 1.2 Integração no Menu



**âœ… Menu Principal:**

- Botão: **"â€šÃ»ï Incluir Novo Exame"** (services/menu_handler.py, linha 46)

- Ação: `self.incluir_novo_exame()` (linha 323)

- Chama: `from ui.cadastros_diversos import CadastrosDiversosWindow` (linha 325)



**â�Œ Problema Identificado:**

- Menu tenta importar de `ui.cadastros_diversos` (linha 325)

- Arquivo real está em `services/cadastros_diversos.py`

- **Import path incorreto â†’ causará erro em runtime**



### 1.3 Arquitetura Implementada



```

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�

â”‚  CadastrosDiversosWindow (Tkinter Toplevel)         â”‚

â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤

â”‚ â€¢ Janela com 4 abas (Exames, Equipamentos,          â”‚

â”‚   Placas, Regras)                                   â”‚

â”‚ â€¢ Tabelas ttk.Treeview para cada tipo               â”‚

â”‚ â€¢ Formulários CTkEntry para edição                  â”‚

â”‚ â€¢ Botões: Novo, Salvar, Excluir, Recarregar        â”‚

â”‚                                                     â”‚

â”‚ Métodos por aba:                                    â”‚

â”‚ â€¢ _build_tab_exames()                               â”‚

â”‚ â€¢ _build_tab_equipamentos()                         â”‚

â”‚ â€¢ _build_tab_placas()                               â”‚

â”‚ â€¢ _build_tab_regras()                               â”‚

â”‚                                                     â”‚

â”‚ Utilitários:                                        â”‚

â”‚ â€¢ _load_csv(key)  â†’ lê arquivo CSV                  â”‚

â”‚ â€¢ _save_csv(key)  â†’ escreve arquivo CSV             â”‚

â”‚ â€¢ _ensure_csv(key) â†’ cria se não existir            â”‚

â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

```



---



## 2. ANÃ�LISE DETALHADA DA IMPLEMENTAÃ‡ÃƒO



### 2.1 Aba "Exames" — Campos



**âœ… Formulário implementado com campos:**

1. **Nome do exame** (entry_exame)

2. **Módulo de análise** (entry_modulo)

3. **Tipo de placa** (entry_tipo_placa)

4. **Número/ID do kit** (entry_numero_kit)

5. **Equipamento associado** (entry_equipamento_exame)



**Operações:**

- Carregar lista de exames (treeview) — âœ…

- Selecionar exame â†’ preench formulário — âœ…

- Novo exame â†’ limpar formulário — âœ…

- Salvar exame â†’ atualizar CSV — âœ…

- Excluir exame â†’ remover de CSV — âœ…



**Exemplo de fluxo:**

```

Usuário clica "Novo Exame"

  â†’ current_exam_id = None

  â†’ formulário fica vazio



Usuário preenche:

  exame = "VR1e2 Biomanguinhos 7500"

  modulo_analise = "analise.vr1e2_biomanguinhos_7500.analisar_placa_vr1e2_7500"

  tipo_placa = "48"

  numero_kit = "1140"

  equipamento = "7500 Real-Time"



Usuário clica "Salvar"

  â†’ dados adicionados à lista exames_config.csv

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



### 2.3 Persistência



**âœ… CSV Read/Write:**

```python

def _load_csv(self, key: str) -> List[Dict[str, str]]:

    # Lê CSV com encoding UTF-8, retorna list of dicts

    

def _save_csv(self, key: str, rows: List[Dict[str, str]]) -> None:

    # Escreve CSV com headers, encoding UTF-8

```



**âœ… Logging:**

- Cada operação registrada em `services/logger.py`



---



## 3. LACUNAS E DEFICIÃŠNCIAS (â�Œ Status Fase 5)



### 3.1 **NÃƒO Implementado: Integração com Registry JSON**



**Requisito da Fase 5:**

> Tela "Gerenciar Exames": lista exames carregados; **formulário Novo/Editar com campos do schema**; validar e salvar em **config/exams/<slug>.json**; **recarregar registry**.



**O que falta:**



| Requisito | Status | Detalhe |

|-----------|--------|---------|

| **Aba "Gerenciar Exames" (novo/editar)** | â�Œ | Atual aba "Exames" só edita CSV, não JSON |

| **Formulário com schema ExamConfig** | â�Œ | Formulário não tem campos: alvos, mapa_alvos, faixas_ct, rps, export_fields, panel_tests_id, controles |

| **Salvar em config/exams/<slug>.json** | â�Œ | Salva apenas em banco/exames_config.csv; sem geração de JSON |

| **Validação de schema** | â�Œ | Sem validação de faixas_ct (detect_max, inconc_min, inconc_max) |

| **Recarregar registry** | â�Œ | Sem integração com `services.exam_registry.registry.load()` |

| **UI para campos JSON** | â�Œ | Sem form fields para alvos/mapa_alvos/export_fields |



### 3.2 **Erro no Menu Handler**



**Problema:**

```python

# services/menu_handler.py, linha 325 (INCORRETO)

from ui.cadastros_diversos import CadastrosDiversosWindow

```



**Realidade:**

- Arquivo está em `services/cadastros_diversos.py`

- Import correto deveria ser: `from services.cadastros_diversos import CadastrosDiversosWindow`



**Impacto:** Menu button "Incluir Novo Exame" falhará com `ModuleNotFoundError`



### 3.3 **Duplicação Potencial**



Se menu correto, usuário pode editar **duas fontes:**

1. **CSV** (`banco/exames_config.csv`) — via UI atual

2. **JSON** (`config/exams/<slug>.json`) — fonte de verdade da Fase 3



**Inconsistência:** Usuário edita exame no CSV, mas registry carrega JSON sobrescrevendo. Mudanças no CSV perdidas.



---



## 4. O QUE A FASE 5 DEVERIA SER



### 4.1 Tela "Gerenciar Exames" Completa



**Layout proposto:**

```

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�

â”‚  Gerenciar Exames — Registry Editor                    â”‚

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

â”‚  [Básico] [Alvos] [Faixas CT] [RP] [Export] [Controles]â”‚

â”‚                                                        â”‚

â”‚  â”Œâ”€ Básico â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�         â”‚

â”‚  â”‚ Nome Exame:          [____________]      â”‚         â”‚

â”‚  â”‚ Slug:                [____________]      â”‚         â”‚

â”‚  â”‚ Equipamento:         [____________]      â”‚         â”‚

â”‚  â”‚ Tipo Placa:          [48 â–¼]              â”‚         â”‚

â”‚  â”‚ Esquema Agrupamento: [96->48 â–¼]          â”‚         â”‚

â”‚  â”‚ Kit Código:          [____________]      â”‚         â”‚

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

detect_max:    [38.0 ]  â†� CT máximo detectável

inconc_min:    [38.01]  â†� CT mínimo inconclusivo

inconc_max:    [40.0 ]  â†� CT máximo inconclusivo

rp_min:        [15.0 ]  â†� CT mínimo referência positiva

rp_max:        [35.0 ]  â†� CT máximo referência positiva

```



**Aba "Export Fields":**

```

Analitos a exportar (separados por ;):

[Sars-Cov-2; Influenzaa; influenzab; RSV; adenovírus; ...]



Panel Tests ID:

[1 ]



Kit Código:

[1140 ]

```



**Aba "Controles":**

```

Controles Negativos (CN) — poços:

[G11+G12]



Controles Positivos (CP) — poços:

[H11+H12]

```



### 4.3 Fluxo de Salva Proposto



```

Usuário clica [Salvar]

  â†“

Validar campos:

  â€¢ nome_exame: obrigatório

  â€¢ tipo_placa: número válido

  â€¢ faixas_ct.detect_max < inconc_min < inconc_max

  â€¢ alvos: lista não vazia (se seção editada)

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



**Arquivo:** `services/cadastros_diversos.py` — adicionar nova aba



**Classe auxiliar:**

```python

@dataclass

class RegistryExamEditor:

    """Gerencia edição de exames via JSON + Registry"""

    

    def load_exam(self, slug: str) -> ExamConfig:

        """Carrega exame do registry"""

        

    def save_exam(self, exam_cfg: ExamConfig) -> None:

        """Salva ExamConfig em config/exams/{slug}.json"""

        

    def validate_exam(self, exam_cfg: ExamConfig) -> Tuple[bool, str]:

        """Valida schema ExamConfig"""

        

    def reload_registry(self) -> None:

        """Recarrega registry após salvar"""

```



**UI Components:**

- Listbox com exames carregados do registry

- Multi-aba form (Básico, Alvos, Faixas CT, RP, Export, Controles)

- Botões: Novo, Editar, Excluir, Salvar, Cancelar, Recarregar Registry

- Validação de entrada em tempo real



### 5.3 Cronograma Estimado



| Tarefa | Esforço | Prioridade |

|--------|---------|-----------|

| Fix import menu_handler | 5 min | ğŸ”´ **CRÃ�TICA** |

| Criar ui/cadastros_diversos.py (alias) | 2 min | ğŸŸ¡ Alta |

| Adicionar classe RegistryExamEditor | 2 horas | ğŸŸ¡ Alta |

| Build UI multi-aba com CTkTabview | 3 horas | ğŸŸ¡ Alta |

| Implementar _build_registry_form() | 2 horas | ğŸŸ¡ Alta |

| Integrar validação de schema | 1 hora | ğŸŸ¡ Alta |

| Testar CRUD JSON + reload registry | 1 hora | ğŸŸ¡ Alta |

| **Total estimado** | **~9-10 horas** | |



---



## 6. CHECKLIST DA FASE 5



### Status Atual (Before):



- [ ] Tela "Gerenciar Exames" lista exames carregados

- [ ] Formulário com campos do schema ExamConfig

- [ ] Novo/Editar exame

- [ ] Validar dados (schema, faixas CT)

- [ ] Salvar em `config/exams/<slug>.json`

- [ ] Recarregar registry automaticamente

- [ ] Mensagens de sucesso/erro



### Implementado Atualmente:



- [x] UI básica com 4 abas (CSV CRUD — não JSON)

- [x] Botões Novo, Salvar, Excluir, Recarregar

- [x] Persistência em CSV

- [x] Integração no menu



### Faltando (Para Completude):



- [ ] Integração com `exam_registry.py` (**CRÃ�TICA**)

- [ ] Aba "Gerenciar Exames" (registry, não CSV)

- [ ] Formulário multi-aba para ExamConfig

- [ ] JSON save/load para `config/exams/`

- [ ] Validação de faixas_ct

- [ ] Registry reload após salvar

- [ ] Tratamento de slug duplicado

- [ ] Tests para CRUD JSON



---



## 7. COMPARAÃ‡ÃƒO: Implementado vs. Requisito



| Requisito Fase 5 | Implementado | Faltando |

|------------------|--------------|----------|

| **Tela "Gerenciar Exames"** | âœ… Parcial (CSV) | â�Œ JSON/Registry |

| **Lista exames carregados** | âœ… Sim (CSV) | âš ï¸� Deveria vir do registry |

| **Formulário com campos schema** | â�Œ Não | âš ï¸� Precisa de 13 campos + validação |

| **Novo/Editar exame** | âœ… Sim (CSV) | â�Œ JSON não |

| **Validar dados** | âš ï¸� Mínimo | â�Œ Schema validation |

| **Salvar em config/exams/<slug>.json** | â�Œ Não | âš ï¸� Deveria ser JSON, não CSV |

| **Recarregar registry** | â�Œ Não | âš ï¸� Precisaria registry.load() |



---



## 8. RECOMENDAÃ‡Ã•ES



### ğŸ”´ **Crítico (Fazer Primeiro):**



1. **Fix import path** — menu_handler.py linha 325

   ```python

   from services.cadastros_diversos import CadastrosDiversosWindow  # â†� corrigir

   ```



2. **Criar alias em ui/** — evitar duplicação

   ```python

   # ui/cadastros_diversos.py (novo arquivo)

   from services.cadastros_diversos import CadastrosDiversosWindow

   ```



### ğŸŸ¡ **Importante (Para completar Fase 5):**



3. **Estender CadastrosDiversosWindow** — adicionar aba "Exames (Registry)"

   - Listar exames do registry (`ExamRegistry.exams.keys()`)

   - Formulário multi-aba para ExamConfig

   - Save JSON + reload registry



4. **Criar RegistryExamEditor class** — separar lógica de UI

   - Load/save ExamConfig

   - Validate schema

   - Handle file I/O



### ğŸŸ¢ **Nice-to-have:**



5. Suporte a YAML além de JSON

6. Importação de exames de arquivo (upload ZIP com JSONs)

7. Exportação de configuração (backup)

8. Validação visual em tempo real



---



## 9. CONCLUSÃƒO



**Fase 5 — Status: âš ï¸� PARCIALMENTE IMPLEMENTADO**



âœ… **O que existe:**

- UI funcional com 4 abas (Exames, Equipamentos, Placas, Regras)

- CRUD em CSV

- Integração no menu principal

- Persistência e logging



â�Œ **O que falta (essencial para Fase 5 completa):**

- **Integração com Registry JSON** — todo requisito central da Fase 5

- Formulário com campos do schema ExamConfig

- Save em `config/exams/<slug>.json`

- Recarregar registry após salvar

- Validação de schema completa



**Ação recomendada:**

1. Fix import crítico (5 min)

2. Criar nova aba "Exames (Registry)" com formulário multi-aba (~9-10 horas)

3. Testar fluxo completo: novo exame â†’ JSON â†’ registry reload



**Prioridade:** Alta — Fase 5 é bloqueante para UI gerenciável de exames.



