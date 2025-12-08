# ğŸ—ºï¸� PLANO EM VISÃƒO GERAL — FASE 5



**Objetivo:** Implementar UI de cadastro/edição de exames com registry integration  

**Tempo Total:** 11-12 horas  

**Distribuição:** 2-3 dias  



---



## ğŸ“Š ESTRUTURA DO PLANO



```

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�

â”‚ FASE 5 — 6 ETAPAS SEQUENCIAIS                                  â”‚

â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜



â”Œâ”€ ETAPA 1 (1-2h) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�

â”‚ Preparação & Design                               â”‚

â”‚ â€¢ Ler docs + código                               â”‚

â”‚ â€¢ Entender schema ExamConfig                      â”‚

â”‚ â€¢ Sketchar UI                                     â”‚

â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

         â†“

â”Œâ”€ ETAPA 2 (2h) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�

â”‚ Classe RegistryExamEditor                          â”‚

â”‚ â€¢ 7 métodos auxiliares                            â”‚

â”‚ â€¢ Load/Save/Validate/Delete                       â”‚

â”‚ â€¢ Registry reload                                 â”‚

â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

         â†“

â”Œâ”€ ETAPA 3 (2h) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�

â”‚ UI Aba "Exames (Registry)"                         â”‚

â”‚ â€¢ Listbox com exames                              â”‚

â”‚ â€¢ Botões: Novo, Editar, Excluir, Recarregar      â”‚

â”‚ â€¢ Status label                                    â”‚

â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

         â†“

â”Œâ”€ ETAPA 4 (3h) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�

â”‚ Formulário Multi-Aba (6 abas, 13+ campos)         â”‚

â”‚ â€¢ Aba 1: Básico (6 campos)                        â”‚

â”‚ â€¢ Aba 2: Alvos (2 campos)                         â”‚

â”‚ â€¢ Aba 3: Faixas CT (5 campos)                     â”‚

â”‚ â€¢ Aba 4: RP (1 campo)                             â”‚

â”‚ â€¢ Aba 5: Export (2 campos)                        â”‚

â”‚ â€¢ Aba 6: Controles (2 campos)                     â”‚

â”‚ â€¢ Collect data + Salvar                           â”‚

â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

         â†“

â”Œâ”€ ETAPA 5 (2h) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�

â”‚ Integração JSON + Registry Reload                 â”‚

â”‚ â€¢ Save em config/exams/{slug}.json                â”‚

â”‚ â€¢ Chamar registry.load()                          â”‚

â”‚ â€¢ Atualizar UI                                    â”‚

â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

         â†“

â”Œâ”€ ETAPA 6 (1-2h) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�

â”‚ Testes & Polimento                                â”‚

â”‚ â€¢ Pytest cases (~5 testes)                        â”‚

â”‚ â€¢ Testes manuais (UI integração)                  â”‚

â”‚ â€¢ Error handling                                  â”‚

â”‚ â€¢ Refine visual                                   â”‚

â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜



             â†“â†“â†“ FASE 5 COMPLETA â†“â†“â†“

```



---



## ğŸ�¯ ETAPAS RESUMIDAS



| Etapa | Foco | Tempo | Tarefas |

|-------|------|-------|---------|

| **1** | Preparação | 1-2h | Ler docs, revisar código, design |

| **2** | Backend | 2h | Criar classe RegistryExamEditor |

| **3** | UI Básica | 2h | Adicionar aba ao TabView |

| **4** | UI Complexa | 3h | Formulário multi-aba (6 abas) |

| **5** | Integração | 2h | JSON save + registry reload |

| **6** | QA | 1-2h | Testes + polimento |

| **TOTAL** | | **11-12h** | **Fase 5 Completa** |



---



## ğŸ“ˆ FLUXO DE DADOS (O que vai acontecer)



```

ANTES (Atual):

User â†’ Menu Button â†’ CadastrosDiversosWindow

         â†“

      4 abas CSV CRUD (não registry)

         â†“

      Salva CSV



DEPOIS (Fase 5 Completo):

User â†’ Menu Button â†’ CadastrosDiversosWindow

         â†“

      NEW: 5ª aba "Exames (Registry)"

         â†“

      Listbox com exames do registry

         â†“

      [Novo] â†’ ExamFormDialog (6 abas, 13 campos)

         â†“

      Validação de schema

         â†“

      Save em config/exams/{slug}.json

         â†“

      registry.load() recarrega

         â†“

      UI atualizada (listbox reflete novo exame)

```



---



## ğŸ”‘ COMPONENTES PRINCIPAIS



### âœ… O que vai ser criado/modificado:



1. **Classe RegistryExamEditor** (new, ~200 linhas)

   - load_all_exams()

   - load_exam(slug)

   - save_exam(cfg)

   - delete_exam(slug)

   - validate_exam(cfg)

   - reload_registry()



2. **Classe ExamFormDialog** (new, ~400 linhas)

   - 6 CTkTabview abas

   - _build_tab_*() (x6)

   - _collect_form_data()

   - _salvar()



3. **UI em CadastrosDiversosWindow** (modified, ~150 linhas)

   - _build_tab_exames_registry()

   - _abrir_formulario_exame()

   - _novo_exame_registry()

   - _editar_exame_registry()

   - _excluir_exame_registry()

   - _recarregar_registry()

   - _carregar_exames_registry()

   - _on_select_exam_registry()



4. **Testes** (new, ~150 linhas)

   - tests/test_fase5_registry_editor.py

   - 5+ casos de teste (pytest)



**Total novo código:** ~900 linhas



---



## â�±ï¸� CRONOGRAMA RECOMENDADO



### ğŸ“… DIA 1 (4 horas)



```

09:00 — 10:30  ETAPA 1 (1.5h)

               âœ“ Ler documentação

               âœ“ Revisar código existente

               âœ“ Entender schema + design



10:30 — 12:30  ETAPA 2 (2h)

               âœ“ Criar RegistryExamEditor

               âœ“ Implementar 7 métodos

               âœ“ Testes import



12:30 — 14:00  ETAPA 3 (1.5h)

               âœ“ Adicionar aba "Exames (Registry)"

               âœ“ Listbox + buttons

               âœ“ Callbacks básicos

```



### ğŸ“… DIA 2 (4 horas)



```

09:00 — 12:00  ETAPA 4 (3h)

               âœ“ Criar ExamFormDialog

               âœ“ 6 abas com widgets

               âœ“ Data collection + save



12:00 — 14:00  ETAPA 5 (2h)

               âœ“ Integrar JSON save

               âœ“ Registry reload

               âœ“ Testes básicos

```



### ğŸ“… DIA 3 (3-4 horas)



```

09:00 — 10:30  ETAPA 6a (1.5h)

               âœ“ Pytest cases

               âœ“ Edge cases



10:30 — 12:30  ETAPA 6b (2h)

               âœ“ Testes manuais UI

               âœ“ Error handling

               âœ“ Polimento visual



12:30 — 13:30  Finalização (1h)

               âœ“ Documentação

               âœ“ Verificação checklist

               âœ“ Marcar completo

```



**Total: 11-12 horas distribuídas em 2.5-3 dias**



---



## ğŸ“‹ CHECKLIST POR ETAPA



### âœ… ETAPA 1: Preparação (1-2h)



```

LEITURA:

[ ] RELATORIO_FASE5_ANALISE.md seções 1-4

[ ] services/exam_registry.py linhas 55-90

[ ] services/cadastros_diversos.py (completo)

[ ] config/exams/vr1e2_biomanguinhos_7500.json



ENTENDIMENTO:

[ ] ExamConfig dataclass (15 campos + 2 métodos)

[ ] Fluxo: Novo â†’ Validate â†’ Save JSON â†’ Reload Registry

[ ] Schema validation (faixas_ct, alvos, etc)

[ ] Registry hybrid load (CSV+JSON)



DESIGN:

[ ] Sketchar layout aba "Exames (Registry)"

[ ] Definir campos para cada aba (6 abas, 13 campos)

[ ] Entender widgets: Entry, Text, Combobox, Listbox

```



### âœ… ETAPA 2: RegistryExamEditor (2h)



```

IMPLEMENTAR:

[ ] @dataclass RegistryExamEditor

[ ] load_all_exams() â†’ List[Tuple[nome, slug]]

[ ] load_exam(slug) â†’ ExamConfig | None

[ ] save_exam(cfg) â†’ Tuple[bool, str]

[ ] delete_exam(slug) â†’ Tuple[bool, str]

[ ] validate_exam(cfg) â†’ Tuple[bool, str]

[ ] reload_registry() â†’ None

[ ] _exam_to_dict(cfg) â†’ Dict



TESTAR:

[ ] Imports funcionam (from services.cadastros_diversos import RegistryExamEditor)

[ ] Registry.load() chamado

[ ] Exames carregados corretamente

```



### âœ… ETAPA 3: UI Aba Registry (2h)



```

IMPLEMENTAR:

[ ] self.tabview.add("Exames (Registry)")

[ ] _build_tab_exames_registry() (~120 linhas)

[ ] Listbox com load_all_exams()

[ ] Botões: [Novo] [Editar] [Excluir] [Recarregar]

[ ] Status label

[ ] _on_select_exam_registry()

[ ] _carregar_exames_registry()



TESTAR:

[ ] Aba aparece no TabView

[ ] Listbox carrega exames (â‰¥4)

[ ] Seleção funciona

[ ] Status atualiza

```



### âœ… ETAPA 4: Formulário Multi-Aba (3h)



```

IMPLEMENTAR:

[ ] Classe ExamFormDialog (~400 linhas)

[ ] _build_tab_basico() — 6 campos (Entry widgets)

[ ] _build_tab_alvos() — 2 campos (Text widget)

[ ] _build_tab_faixas() — 5 campos (Entry floats)

[ ] _build_tab_rp() — 1 campo (Text widget)

[ ] _build_tab_export() — 2 campos (Text + Entry)

[ ] _build_tab_controles() — 2 campos (Text widgets)

[ ] _collect_form_data() — retorna ExamConfig

[ ] _salvar() — valida + save + reload + callback



TESTAR:

[ ] Dialog abre (Novo Exame)

[ ] 6 abas navegáveis

[ ] Dados preenchidos se editando

[ ] Collect data funciona

```



### âœ… ETAPA 5: Integração JSON (2h)



```

IMPLEMENTAR:

[ ] _on_exame_salvo() callback

[ ] JSON salvo em config/exams/{slug}.json

[ ] registry.load() chamado após save

[ ] Listbox atualizado

[ ] Status message exibida

[ ] Error handling funciona



TESTAR:

[ ] Novo exame â†’ JSON criado

[ ] Registry recarregado

[ ] Exame aparece no listbox

[ ] Editar exame â†’ JSON atualizado

[ ] Deletar exame â†’ Arquivo removido

```



### âœ… ETAPA 6: Testes & Polimento (1-2h)



```

TESTES:

[ ] tests/test_fase5_registry_editor.py criado

[ ] test_load_all_exams() PASSA

[ ] test_validate_exam_valid() PASSA

[ ] test_validate_exam_invalid() PASSA

[ ] test_save_exam() PASSA

[ ] test_delete_exam() PASSA

[ ] pytest -v âœ“ (5/5 PASSA)



TESTES MANUAIS:

[ ] Menu button funciona

[ ] Novo exame â†’ Dialog â†’ 6 abas â†’ Save â†’ Registry

[ ] Editar exame existente

[ ] Excluir exame

[ ] Validação rejeita inválido

[ ] Recarregar Registry atualiza UI



POLIMENTO:

[ ] Mensagens de erro claras

[ ] Tooltips em campos obrigatórios

[ ] Cores indicando status

[ ] Sem warnings em console

[ ] UI responsivo (não congela)

```



---



## ğŸ�� DELIVERABLES



### Código



1. **RegistryExamEditor class** (~200 linhas)

   - Implementação: `services/cadastros_diversos.py`

   - Testes: `tests/test_fase5_registry_editor.py`



2. **ExamFormDialog class** (~400 linhas)

   - Implementação: `services/cadastros_diversos.py`



3. **UI methods** (~150 linhas)

   - Implementação: `services/cadastros_diversos.py`

   - Métodos adicionados a `CadastrosDiversosWindow`



### Funcionalidades



1. âœ… Aba "Exames (Registry)" no TabView

2. âœ… Listbox mostrando todos exames

3. âœ… Dialog "Novo/Editar" com 6 abas, 13 campos

4. âœ… Validação de schema ExamConfig

5. âœ… Save JSON em `config/exams/<slug>.json`

6. âœ… Registry reload integrado

7. âœ… Editar/Deletar exames

8. âœ… Testes unitários (pytest)



### Documentação



1. âœ… PLANO_FASE5_ETAPAS.md (este arquivo)

2. âœ… TODO.md atualizado â†’ Fase 5 = FEITO

3. âœ… LEITURA_5MIN.md â†’ Fase 5 status = 100%

4. âœ… Código com docstrings completas



---



## âœ¨ RESULTADO FINAL



**Quando Fase 5 estar completa:**



```

User Experience:

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”�

â”‚ Menu â†’ "Incluir Novo Exame"           â”‚

â”‚         â†“                              â”‚

â”‚  CadastrosDiversosWindow               â”‚

â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”� â”‚

â”‚  â”‚ [Exames] [Equipamentos] [...]    â”‚ â”‚

â”‚  â”‚ [Exames (Registry)]  â†� NEW!      â”‚ â”‚

â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚

â”‚         â†“                              â”‚

â”‚  Exames do Registry (Listbox):         â”‚

â”‚  â€¢ VR1e2 Biomanguinhos 7500           â”‚

â”‚  â€¢ ZDC Biomanguinhos 7500             â”‚

â”‚  â€¢ VR1                                 â”‚

â”‚  â€¢ VR2                                 â”‚

â”‚         â†“                              â”‚

â”‚  [Novo] â†’ Dialog (6 abas)             â”‚

â”‚  Tab: [Básico] [Alvos] [Faixas]...   â”‚

â”‚  Preencher 13 campos                   â”‚

â”‚  [Salvar] â†’ âœ“ Sucesso!                â”‚

â”‚         â†“                              â”‚

â”‚  Novo exame em config/exams/           â”‚

â”‚  Registry recarregado                  â”‚

â”‚  Listbox atualizado (reflete novo)    â”‚

â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜



System State:

âœ“ Código: 750+ linhas novas

âœ“ Testes: 5+ pytest cases passam

âœ“ Funcionalidade: CRUD JSON completo

âœ“ Integração: Registry fully working

âœ“ Validação: Schema enforcement

âœ“ UI: Polida e responsiva

```



---



## ğŸ“� PRÃ“XIMOS PASSOS



1. **Imediato:** Salve este plano (`PLANO_FASE5_ETAPAS.md`)

2. **Dia 1 Manhã:** Comece ETAPA 1 (Preparação)

3. **Dia 1 Tarde:** Comece ETAPA 2 (RegistryExamEditor)

4. **Dia 2:** ETAPA 4 (Formulário) — a mais complexa

5. **Dia 3:** ETAPA 6 (Testes)

6. **Fim:** Marque TODO.md Fase 5 = âœ… COMPLETO



---



## ğŸ�¯ SUCESSO = Quando?



Fase 5 está **COMPLETA** quando:



- âœ… Aba "Exames (Registry)" criada e funcional

- âœ… Novo exame â†’ Dialog 6-aba â†’ JSON save â†’ Registry reload

- âœ… Editar exame â†’ Preench fields â†’ Update JSON

- âœ… Deletar exame â†’ Confirm â†’ Remove JSON

- âœ… Validação rejeita inválido

- âœ… Todos testes passam (pytest)

- âœ… TODO.md marcado FEITO

- âœ… Sistema pronto para produção



**Prioridade:** ğŸ”´ **ALTA**  

**Tempo Estimado:** 11-12 horas  

**Bloqueante:** Sim (para UI completa)



---



Boa sorte! ğŸš€



