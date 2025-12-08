# 📋 PLANO DE IMPLANTAÇÃO - FASES DEFINIDAS

**Data:** 2025-12-07  
**Versão:** 1.0  
**Status:** Pronto para implementação

---

## 🎯 VISÃO GERAL

Plano estruturado em **5 fases**, cada uma com:
- ✅ Objetivos claros
- 📊 Componentes específicos
- ⏱️ Duração estimada
- 🧪 Testes necessários
- ✔️ Critério de aceição

---

## 📊 CRONOGRAMA RESUMIDO

```
FASE 1: Fundação (Semana 1-2)     Auto-detecção + Equipment Registry
FASE 2: Análise (Semana 2-3)      Parser de fórmulas + Rules engine
FASE 3: Resultados (Semana 3-4)   Janela gráfica de resultados
FASE 4: Integração (Semana 4-5)   Fluxo completo sincronizado
FASE 5: Refinamento (Semana 5-6)  Testes E2E + Otimização
```

---

## 🔴 FASE 1: FUNDAÇÃO (Semana 1-2)

### 📌 OBJETIVO
Implementar detecção automática de equipamento e criação do Equipment Registry

### 📦 COMPONENTES A CRIAR

#### **1.1 - Equipment Detector**
```
services/equipment_detector.py (300-400 linhas)

Responsabilidades:
├─ Ler arquivo XLSX
├─ Analisar estrutura (headers, colunas, linhas)
├─ Comparar com padrões conhecidos
├─ Retornar top 3 matches com scores
└─ Permitir override manual

Funções principais:
├─ detectar_equipamento(caminho_arquivo) → Equipamento | None
├─ analisar_estrutura_xlsx(arquivo) → Dict estrutura
├─ calcular_match_score(estrutura, padrão) → float (0-100)
└─ obter_padroes_conhecidos() → List[padrão]

Entrada: arquivo XLSX
Saída: {
    "equipamento": "7500 Real-Time",
    "confianca": 95.5,
    "alternativas": [
        {"equipamento": "CFX96", "confianca": 3.2},
        {"equipamento": "QuantStudio", "confianca": 1.3}
    ],
    "estrutura_detectada": {
        "coluna_well": "A",
        "coluna_target": "C",
        "coluna_ct": "D",
        "linha_inicio": 5,
        "headers": ["Well", "Sample", "Target", "Ct"]
    }
}

Padrões conhecidos (banco de dados):
├─ 7500 Real-Time:
│  ├─ Headers: Well, Sample Name, Target, Cq
│  ├─ Colunas: A, B, C, D
│  ├─ Linha início: 5
│  └─ Validações: Well em formato A01
│
├─ CFX96:
│  ├─ Headers: diferentes (Bio-Rad)
│  ├─ Colunas: A, E, F
│  ├─ Linha início: 3
│  └─ Validações: outra formatação
│
└─ QuantStudio:
   ├─ Headers: outro padrão
   ├─ Colunas: B, D, E
   ├─ Linha início: 8
   └─ Validações: outro formato
```

#### **1.2 - Equipment Registry**
```
services/equipment_registry.py (200-300 linhas)

Responsabilidades:
├─ Carregar config de equipamentos
├─ Manter mapeamento máquina → padrão XLSX
├─ Fornecer extrator específico
└─ Validar estrutura

Classe: EquipmentRegistry
├─ equipamentos: Dict[str, EquipmentConfig]
├─ load() → carrega de banco/equipamentos.csv
├─ get(nome) → EquipmentConfig
└─ registrar_novo(config) → adiciona

EquipmentConfig dataclass:
├─ nome: str ("7500 Real-Time")
├─ modelo: str ("Applied Biosystems")
├─ tipo_placa: int (48, 96, 36)
├─ xlsx_estrutura: Dict
│  ├─ coluna_well: str ("A")
│  ├─ coluna_sample: str ("B")
│  ├─ coluna_target: str ("C")
│  ├─ coluna_ct: str ("D")
│  ├─ linha_inicio_dados: int (5)
│  ├─ validacoes: List[str]
│  └─ delimitador: str (",")
├─ extrator_nome: str ("extrair_7500")
└─ formatador_nome: str ("formatar_7500")

Banco de dados (banco/equipamentos.csv):
├─ Colunas: nome, modelo, fabricante, tipo_placa, xlsx_config
├─ Exemplo 1:
│  nome: "7500 Real-Time"
│  modelo: "Applied Biosystems 7500"
│  fabricante: "Thermo Fisher"
│  tipo_placa: 96
│  xlsx_config: (JSON encoded)
│  {
│    "coluna_well": "A",
│    "coluna_sample": "B",
│    "coluna_target": "C",
│    "coluna_ct": "D",
│    "linha_inicio": 5,
│    "validacoes": ["well_format_a01", "target_not_null"]
│  }
└─ Exemplo 2: CFX96, etc
```

#### **1.3 - Extractores Específicos por Equipamento**
```
services/equipment_extractors.py (400-500 linhas)

Responsabilidades:
├─ Ler arquivo XLSX conforme padrão
├─ Normalizar para formato padrão
├─ Validar dados
└─ Retornar DataFrame limpo

Funções:
├─ extrair_7500(caminho_arquivo, config) → DataFrame
├─ extrair_cfx96(caminho_arquivo, config) → DataFrame
├─ extrair_quantstudio(caminho_arquivo, config) → DataFrame
└─ extrair_generico(caminho_arquivo, config) → DataFrame

Cada extrator:
1. Abre arquivo XLSX
2. Lê estrutura conforme config
3. Valida: colunas presentes? Linha início correta?
4. Normaliza nomes (Well → bem, Target → alvo, Ct → ct)
5. Converte tipos: CT → float, Well → string
6. Remove linhas vazias
7. Retorna DataFrame padrão:
   └─ Colunas: bem, amostra, alvo, ct
      bem: A01, A02, ...
      amostra: nome da amostra
      alvo: nome do alvo (SC2, HMPV, etc)
      ct: valor numérico ou null
```

### 🧪 TESTES FASE 1

```
teste_equipment_detector.py:
├─ Test 1: Detectar 7500 Real-Time corretamente ✓
├─ Test 2: Detectar CFX96 corretamente ✓
├─ Test 3: Detectar QuantStudio corretamente ✓
├─ Test 4: Retornar scores corretos ✓
└─ Test 5: Permitir override manual ✓

teste_equipment_registry.py:
├─ Test 1: Carregar equipamentos do CSV ✓
├─ Test 2: get() retorna config correta ✓
├─ Test 3: Registrar novo equipamento ✓
└─ Test 4: Validar estrutura ✓

teste_extractores.py:
├─ Test 1: extrair_7500() normaliza corretamente ✓
├─ Test 2: extrair_cfx96() normaliza corretamente ✓
├─ Test 3: extrair_quantstudio() normaliza corretamente ✓
├─ Test 4: Validações funcionam ✓
├─ Test 5: Tipos de dados corretos ✓
└─ Test 6: Linhas vazias removidas ✓
```

### ✅ CRITÉRIO DE ACEITAÇÃO FASE 1

```
✅ Auto-detecção funciona com 95%+ confiança
✅ Equipment Registry carregado e funcionando
✅ Extractores normalizando dados corretamente
✅ Todos os testes passando
✅ Documentação atualizada
✅ Integração com extracao/busca_extracao.py pronta
```

### 🔗 INTEGRAÇÃO COM CÓDIGO EXISTENTE

```
extracao/busca_extracao.py (REFATORAR):
└─ Após user abrir arquivo:
   ├─ equipment_detector.detectar_equipamento(arquivo)
   ├─ System exibe: "Detectei: 7500 Real-Time (95%)"
   ├─ User: [✓ Confirmar] ou [Selecionar outro]
   ├─ equipamento_selecionado = confirmado
   └─ Armazena em: app_state.equipamento_detectado
      
│ Após user mapear placa:
   ├─ equipment_config = EquipmentRegistry.get(equipamento)
   ├─ extrator = obter_extrator(equipamento)
   └─ Tudo pronto para FASE 2

SAÍDA FASE 1:
├─ app_state.dados_extracao = DataFrame
├─ app_state.parte_placa = 1 ou 2
├─ app_state.equipamento_detectado = "7500 Real-Time"
├─ app_state.equipment_config = EquipmentConfig
└─ app_state.extrator_selecionado = função
```

---

## 🔵 FASE 2: ANÁLISE (Semana 2-3)

### 📌 OBJETIVO
Implementar parser de fórmulas e engine de regras para lógica condicional

### 📦 COMPONENTES A CRIAR

#### **2.1 - Formula Parser**
```
services/formula_parser.py (250-350 linhas)

Responsabilidades:
├─ Parsing de expressões matemáticas
├─ Substituição de variáveis
├─ Avaliação segura
└─ Tratamento de erros

Função principal:
├─ avaliar_formula(expressão: str, variáveis: Dict) → bool | float | str
│  ├─ Entrada: "(CT_DEN1 + CT_DEN2) / 2 < 33", {"CT_DEN1": 15.5, "CT_DEN2": 18.2}
│  ├─ Processamento:
│  │  ├─ Valida variáveis (estão em dict?)
│  │  ├─ Substitui: "(15.5 + 18.2) / 2 < 33"
│  │  ├─ Avalia expressão (safe eval)
│  │  └─ Retorna resultado
│  └─ Saída: true (passou) ou false (não passou)
│
└─ validar_formula(expressão: str) → Resultado validação
   ├─ Símbolos permitidos: +, -, *, /, (, ), <, >, <=, >=, ==, !=, and, or
   ├─ Variáveis: CT_*, resultado_*, flags_*
   ├─ Números: inteiros e floats
   └─ Operadores lógicos: and, or, not

Exemplos de fórmulas suportadas:
├─ "(CT_DEN1 + CT_DEN2) / 2 < 33"  → resultado numérico
├─ "CT_ZIKA < 30 and CT_DENGUE > 15"  → bool
├─ "(CT_ALV1 - CT_ALV2) > 5"  → bool
├─ "CT_SC2 < 38 or resultado_SC2 == 'Inconclusivo'"  → bool
└─ "CT_RP > 15 and CT_RP < 35"  → bool

Segurança:
├─ Whitelist de símbolos permitidos
├─ Sem acesso a funções system (não permite __import__, open, etc)
├─ Timeout de execução (máx 1 segundo)
├─ Try/catch para erros de sintaxe
└─ Log de cada avaliação
```

#### **2.2 - Rules Engine**
```
services/rules_engine.py (300-400 linhas)

Responsabilidades:
├─ Interpretar regras customizadas
├─ Aplicar lógica condicional
├─ Gerar status final
└─ Registrar validações

Tipos de regras suportadas:

1. REGRAS SIMPLES (booleanas):
   └─ "requer_dois_alvos": true
      └─ Valida: count(alvos_positivos) >= 2

2. REGRAS LÓGICAS (estruturadas):
   └─ {
        "tipo": "condicional",
        "descricao": "DEN1 positivo requer DEN2 positivo",
        "condicoes": [
          {"if": "resultado_DEN1 == 'Detectado'",
           "then": "resultado_DEN2 == 'Detectado'"}
        ]
      }

3. REGRAS DE SEQUÊNCIA:
   └─ {
        "tipo": "sequencia",
        "alvos_obrigatorios": ["DEN1", "DEN2"],
        "descracao": "Ambos devem estar presentes"
      }

4. REGRAS DE EXCLUSÃO MÚTUA:
   └─ {
        "tipo": "exlusao_mutua",
        "alvos": ["ZIKA", "DENGUE"],
        "descricao": "Se ZIKA positivo, DENGUE deve ser negativo"
      }

Função principal:
├─ aplicar_regras(regras_dict: Dict, resultados_dict: Dict) → RulesResult
│  ├─ Entrada:
│  │  └─ regras: {
│  │      "requer_dois_alvos": true,
│  │      "formulas": ["(CT_DEN1 + CT_DEN2) / 2 < 33"],
│  │      "condicoes": [...]
│  │    }
│  │  └─ resultados: {
│  │      "alvo_DEN1": {"resultado": "Detectado", "ct": 15.5},
│  │      "alvo_DEN2": {"resultado": "Detectado", "ct": 18.2},
│  │      "alvo_ZIKA": {"resultado": "Não Detectado", "ct": null}
│  │    }
│  │
│  ├─ Processamento:
│  │  ├─ Aplica cada regra
│  │  ├─ Coleta resultados (passou/falhou)
│  │  ├─ Registra detalhes de cada validação
│  │  └─ Gera status geral
│  │
│  └─ Saída: RulesResult = {
│       "status": "válida" | "inválida",
│       "validacoes": [
│         {"regra": "requer_dois_alvos", "resultado": "passou", "detalhes": "2 alvos detectados"},
│         {"regra": "formula_media_ct", "resultado": "passou", "detalhes": "Média 16.85 < 33"}
│       ],
│       "mensagens_erro": []
│     }

RulesResult dataclass:
├─ status: str ("válida", "inválida", "aviso")
├─ validacoes: List[Dict] (cada validação com resultado)
├─ mensagens_erro: List[str]
├─ mensagens_aviso: List[str]
└─ detalhes: str (resumo das validações)
```

#### **2.3 - Integração com UniversalEngine**
```
services/universal_engine.py (REFATORAR):

Novo fluxo no processar_exame():
└─ Após aplicar CT logic básico:
   ├─ 1. CARREGA FÓRMULAS
   │  └─ config.formulas (do ExamRegistry)
   │
   ├─ 2. AVALIA CADA FÓRMULA
   │  └─ formula_parser.avaliar_formula() para cada uma
   │
   ├─ 3. CARREGA REGRAS EXTRA
   │  └─ config.regras_extra (do ExamRegistry)
   │
   ├─ 4. APLICA RULES ENGINE
   │  └─ rules_engine.aplicar_regras(config.regras_extra, resultados)
   │
   ├─ 5. GERA STATUS FINAL
   │  └─ Combina: CT básico + fórmulas + regras
   │
   └─ 6. RETORNA RESULTADO COMPLETO
      ├─ Dados de análise
      ├─ Status de validação
      └─ Detalhes de todas as regras aplicadas

Novo campo em resultado:
├─ resultado_analise: {
│  ├─ status_geral: "válida" | "inválida"
│  ├─ alvos_resultados: {...}
│  ├─ validacoes_aplicadas: [{...}]
│  ├─ mensagens_usuario: [...]
│  └─ pronto_para_envio_gal: bool
```

### 🧪 TESTES FASE 2

```
teste_formula_parser.py:
├─ Test 1: Avaliar "(15.5 + 18.2) / 2 < 33" → true ✓
├─ Test 2: Avaliar "15 < 30 and 35 < 30" → false ✓
├─ Test 3: Validar fórmula válida ✓
├─ Test 4: Rejeitar fórmula com variável inexistente ✓
├─ Test 5: Timeout para expressão infinita ✓
├─ Test 6: Segurança: rejeitar __import__ ✓
└─ Test 7: Tratamento de erro de sintaxe ✓

teste_rules_engine.py:
├─ Test 1: Aplicar regra "requer_dois_alvos" ✓
├─ Test 2: Aplicar regra condicional ✓
├─ Test 3: Aplicar múltiplas regras ✓
├─ Test 4: Gerar RulesResult correto ✓
├─ Test 5: Detalhes de cada validação ✓
└─ Test 6: Mensagens de erro claras ✓

teste_universal_engine_integracao.py:
├─ Test 1: Motor aplica fórmulas ✓
├─ Test 2: Motor aplica regras ✓
├─ Test 3: Status final correto ✓
├─ Test 4: Validações registradas ✓
└─ Test 5: Resultado pronto para FASE 3 ✓
```

### ✅ CRITÉRIO DE ACEITAÇÃO FASE 2

```
✅ Parser de fórmulas funciona corretamente
✅ Rules engine interpreta todas as regras
✅ Segurança validada (sem injeções)
✅ UniversalEngine integrado com parser + rules
✅ Resultado contém status + detalhes de validação
✅ Todos os testes passando
✅ Pronto para passar resultado à janela gráfica
```

---

## 🟢 FASE 3: RESULTADOS (Semana 3-4)

### 📌 OBJETIVO
Criar janela gráfica de resultados editáveis e selecionáveis antes de envio GAL

### 📦 COMPONENTES A CRIAR

#### **3.1 - Tela de Resultados (Janela Modal)**
```
ui/resultado_analise_window.py (600-800 linhas)

Responsabilidades:
├─ Exibir resultados da análise em tabela
├─ Permitir edição de resultados
├─ Permitir seleção de quais enviar
├─ Mostrar status de validação
├─ Confirmação antes de envio

Estrutura da janela:

┌─────────────────────────────────────────────────┐
│ 📊 RESULTADOS DA ANÁLISE                        │
│ Exame: MPX Kit ABC | Data: 2025-12-07 14:30   │
├─────────────────────────────────────────────────┤
│                                                 │
│ 1️⃣  RESUMO DE VALIDAÇÕES                      │
│ ├─ ✅ CT Detectável: PASSOU                    │
│ ├─ ✅ CT Inconclusivo: PASSOU                  │
│ ├─ ✅ Regra 2+ alvos: PASSOU                   │
│ ├─ ✅ Fórmula (CT1+CT2)/2<33: PASSOU          │
│ ├─ ✅ Controle CN: OK                         │
│ ├─ ✅ Controle CP: OK                         │
│ └─ 🟢 STATUS GERAL: VÁLIDA PARA ENVIO         │
│                                                 │
│ 2️⃣  RESULTADOS POR AMOSTRA (EDITÁVEL)        │
│                                                 │
│ Amostra: MPX_001                              │
│ ┌───────────────────────────────────────────┐ │
│ │ Alvo      │ CT    │ Resultado     │ Enviar│ │
│ ├───────────┼───────┼───────────────┼───────┤ │
│ │ DEN1      │ 15.5  │ Detectado     │ ☑    │ │
│ │ DEN2      │ 18.2  │ Detectado     │ ☑    │ │
│ │ ZIKA      │ null  │ Não Detectado │ ☑    │ │
│ │ RP        │ 22.0  │ Válido        │ ☑    │ │
│ └───────────┴───────┴───────────────┴───────┘ │
│                                                 │
│ 📝 EDITAR RESULTADO:                          │
│ Alvo selecionado: DEN1                        │
│ Resultado atual: [Detectado ▼]               │
│ CT atual: [15.5 ]  [Validar novo CT]        │
│                                                 │
│ ⚠️  VALIDAÇÕES:                                │
│ Mudanças no resultado precisam re-validação  │
│ Se mudar DEN1 → Não Detectado:              │
│   └─ Regra "2+ alvos" pode falhar!           │
│                                                 │
│ 3️⃣  CONTROLES                                 │
│ ├─ CN (Controle Negativo):                    │
│ │  └─ CT: 45.0 | Status: ✅ OK (não amplif.) │
│ └─ CP (Controle Positivo):                    │
│    └─ CT: 18.0 | Status: ✅ OK (amplificou)  │
│                                                 │
│ 4️⃣  AÇÕES                                     │
│ [  Salvar edições  ] [  Re-validar  ]        │
│ [  Visualizar PDF  ] [  Cancelar    ]        │
│ [  ✅ Enviar GAL   ]  (habilitado)            │
└─────────────────────────────────────────────────┘

Componentes:

A. SEÇÃO DE VALIDAÇÕES (Read-Only)
   └─ Mostra todas validações aplicadas
   └─ Status: ✅ Passou ou ❌ Falhou
   └─ Detalhes de cada regra

B. TABELA DE RESULTADOS (Editável)
   ├─ Colunas: Alvo | CT | Resultado | Enviar?
   ├─ Linhas: um por alvo + controles
   ├─ CT editável: clique para editar
   ├─ Resultado editável: dropdown
   ├─ Checkbox "Enviar?": seleção individual
   └─ Dupla-clique para inline edit

C. PAINEL DE EDIÇÃO
   ├─ Alvo selecionado
   ├─ CT atual (editor de texto)
   ├─ Resultado (dropdown: Detectado | Não Detectado | Inconclusivo)
   ├─ Botão "Validar novo CT"
   └─ Aviso de impacto de mudanças

D. SEÇÃO DE CONTROLES (Read-Only)
   ├─ CN: CT e status
   ├─ CP: CT e status
   └─ Avisos se inválidos

E. AÇÕES FINAIS
   ├─ [Salvar edições] → Re-valida tudo
   ├─ [Re-validar] → Re-aplica regras com dados editados
   ├─ [Visualizar PDF] → Exibe preview do que será enviado
   ├─ [Cancelar] → Descarta edições
   └─ [✅ Enviar GAL] → Habilita envio (só se válido)
```

#### **3.2 - Gerenciador de Edições e Validação**
```
services/resultado_manager.py (300-400 linhas)

Responsabilidades:
├─ Armazenar dados originais e editados
├─ Detectar mudanças
├─ Re-validar ao editar
├─ Gerar relatório de mudanças
└─ Preparar dados para envio

Classe: ResultadoManager
├─ resultado_original: AnaliseResultado
├─ resultado_atual: AnaliseResultado (cópia editável)
├─ mudancas: List[Mudanca]
├─ validacoes_atuais: RulesResult
│
├─ editar_resultado_alvo(alvo, novo_resultado, novo_ct)
│  └─ Atualiza resultado_atual
│  └─ Registra mudança em mudancas
│  └─ Re-valida automaticamente
│  └─ Retorna: {sucesso, aviso_impacto, validacoes_atualizadas}
│
├─ revalidar() → RulesResult atualizado
│  └─ Aplica parser + rules ao resultado_atual
│  └─ Atualiza validacoes_atuais
│  └─ Retorna novo status
│
├─ gerar_relatorio_mudancas() → str
│  └─ Lista todas mudanças feitas
│
├─ obter_dados_para_envio(alvos_selecionados) → Dict
│  └─ Filtra apenas alvos marcados como "Enviar"
│  └─ Formata para GAL
│  └─ Inclui auditoria de mudanças
│
└─ desfazer_edicoes() → volta ao original

Mudanca dataclass:
├─ alvo: str
├─ campo: str ("resultado" ou "ct")
├─ valor_original: Any
├─ valor_novo: Any
├─ timestamp: datetime
├─ usuario: str
└─ impacto_validacao: str (descrição)
```

#### **3.3 - Integração com MenuHandler**
```
services/menu_handler.py (REFATORAR):

Novo método: realizar_analise() (ATUALIZADO)
├─ 1. User clica "Realizar Análise"
├─ 2. Seleciona exame + lote
├─ 3. Abre arquivo resultado
├─ 4. Sistema DETECTA equipamento (FASE 1)
├─ 5. Sistema EXTRAI e NORMALIZA dados
├─ 6. Motor universal processa
├─ 7. Parser + rules aplicados (FASE 2)
├─ 8. 🆕 ABRE JANELA DE RESULTADOS
│  └─ resultado_analise_window.ResultadoWindow()
│  └─ User vê resultados editáveis
│  └─ User edita se necessário
│  └─ User seleciona quais enviar
│  └─ User clica "Enviar GAL"
│
├─ 9. 🆕 Armazena resultado editado em app_state
│  └─ app_state.resultado_final_validado = resultado
│  └─ app_state.alvos_para_envio = selecionados
│  └─ app_state.status_resultado = "pronto"
│
└─ 10. ✅ Análise completa, pronto para envio

MUDANÇA CRÍTICA:
Antes:
└─ Análise → Salva → Pronto para envio

Agora:
└─ Análise → Janela gráfica (edição) → User confirma → Pronto para envio
```

### 🧪 TESTES FASE 3

```
teste_resultado_window.py:
├─ Test 1: Janela abre com dados corretos ✓
├─ Test 2: Edição de CT funciona ✓
├─ Test 3: Mudança de resultado funciona ✓
├─ Test 4: Re-validação após edição ✓
├─ Test 5: Aviso de impacto de mudança ✓
├─ Test 6: Checkbox "Enviar" funciona ✓
├─ Test 7: Botões habilitados conforme status ✓
└─ Test 8: Cancelar desfaz edições ✓

teste_resultado_manager.py:
├─ Test 1: Armazenar original vs editado ✓
├─ Test 2: Detectar mudanças ✓
├─ Test 3: Re-validar após edição ✓
├─ Test 4: Gerar relatório de mudanças ✓
├─ Test 5: Filtrar dados para envio ✓
└─ Test 6: Desfazer edições ✓

teste_integracao_menu_resultado.py:
├─ Test 1: Fluxo completo análise → resultado ✓
├─ Test 2: Dados fluem corretamente ✓
├─ Test 3: AppState atualizado corretamente ✓
├─ Test 4: Pronto para próxima fase (envio) ✓
└─ Test 5: E2E com diferentes exames ✓
```

### ✅ CRITÉRIO DE ACEITAÇÃO FASE 3

```
✅ Janela gráfica funciona e é intuitiva
✅ Edição de resultados funciona
✅ Re-validação após edição funciona
✅ Seleção de alvos para envio funciona
✅ Avisos de impacto mostrados corretamente
✅ AppState atualizado com dados final
✅ Histórico recebe resultado FINAL (editado)
✅ Todos testes passando
✅ Pronto para integração com envio GAL
```

---

## 🟡 FASE 4: INTEGRAÇÃO (Semana 4-5)

### 📌 OBJETIVO
Sincronizar todas as fases e criar fluxo completo end-to-end

### 📦 COMPONENTES A ATUALIZAR

#### **4.1 - Atualizar Histórico**
```
services/history_report.py (REFATORAR):

Novo campo no registro:
├─ equipamento_detectado: str ("7500 Real-Time")
├─ validacoes_aplicadas: str (JSON de todas validações)
├─ mudancas_usuario: str (JSON de edições realizadas)
├─ alvos_enviados_gal: str (lista separada `;`)
└─ timestamp_edicoes: datetime

Exemplo registro completo:
{
  "id_registro": "550e8400-e29b-41d4-a716-446655440000",
  "data_hora_analise": "2025-12-07 14:30:00",
  "usuario_analise": "joao",
  "exame": "MPX Kit ABC",
  "equipamento_detectado": "7500 Real-Time",  ← NOVO
  "status_analise": "válida",
  "alvo_den1_resultado": "Detectado",
  "alvo_den1_ct": "15.5",
  "alvo_den2_resultado": "Detectado",
  "alvo_den2_ct": "18.2",
  "alvo_zika_resultado": "Não Detectado",
  "alvo_zika_ct": null,
  "validacoes_aplicadas": "{...}",  ← NOVO
  "mudancas_usuario": "{}",  ← NOVO (vazio se não editou)
  "alvos_enviados_gal": "DEN1;DEN2;ZIKA",  ← NOVO
  "status_gal": "não enviado",
  "data_hora_envio": null,
  "usuario_envio": null,
  "sucesso_envio": null,
  "detalhes_envio": null,
  "data_criacao": "2025-12-07 14:30:00"
}
```

#### **4.2 - Atualizar Envio GAL**
```
exportacao/envio_gal.py (REFATORAR):

Novo fluxo:
├─ User clica "Enviar para GAL"
├─ Sistema busca resultados com status_gal = "não enviado"
├─ 🆕 Para cada resultado:
│  ├─ Carrega alvos_enviados_gal (user selecionou quais)
│  ├─ Filtra dados para apenas esses alvos
│  ├─ Carrega mudancas_usuario (sabe quais foram editados)
│  ├─ Inclui auditoria no envio
│  └─ Formata conforme GAL espera
│
├─ Envia para GAL API
├─ Atualiza histórico:
│  ├─ status_gal = "enviado"
│  ├─ data_hora_envio = agora
│  ├─ usuario_envio = usuário logado
│  ├─ sucesso_envio = true
│  └─ detalhes_envio = ID retornado pelo GAL
│
└─ ✅ Completo
```

#### **4.3 - Fluxo Completo Revisado**
```
FLUXO FINAL (COM TODAS FASES):

1️⃣  MAPEAMENTO (FASE 1)
    User: Abre arquivo
    ├─ Auto-detecta equipamento
    ├─ User mapeia placa
    └─ Salva em app_state

2️⃣  ANÁLISE (FASE 1 + 2)
    User: Seleciona exame
    ├─ Auto-detecta equipamento (confirmação)
    ├─ Extrai dados (extrator específico)
    ├─ Motor aplica CT logic
    ├─ Parser avalia fórmulas
    ├─ Rules engine aplica regras
    └─ Gera resultado com validações

3️⃣  REVISÃO E EDIÇÃO (FASE 3)
    Sistema: Abre janela gráfica
    ├─ User vê resultados + validações
    ├─ User pode editar (se necessário)
    ├─ User seleciona quais enviar
    ├─ Sistema re-valida edições
    └─ User clica "Enviar GAL"

4️⃣  HISTÓRICO (FASE 4)
    Sistema: Salva resultado final
    ├─ Inclui: equipamento, validações, edições
    ├─ Status: "não enviado"
    └─ Pronto para envio

5️⃣  ENVIO GAL (FASE 4)
    User: Clica "Envio GAL"
    ├─ Sistema busca "não enviado"
    ├─ Filtra pelos alvos selecionados
    ├─ Envia para GAL API
    ├─ Atualiza status: "enviado"
    └─ ✅ Completo

RESULTADO FINAL:
├─ Histórico rastreia:
│  ├─ Qual equipamento usou
│  ├─ Quais validações foram aplicadas
│  ├─ Quais edições fez user
│  ├─ Quais alvos foi enviado
│  └─ Status completo do envio
│
└─ Sistema é 100% auditável
```

### 🧪 TESTES FASE 4

```
teste_fluxo_completo_e2e.py:
├─ Test 1: Fluxo completo com 7500 ✓
├─ Test 2: Fluxo completo com CFX96 ✓
├─ Test 3: Fluxo completo com QuantStudio ✓
├─ Test 4: Edição + validação + envio ✓
├─ Test 5: Histórico registra equipamento ✓
├─ Test 6: Histórico registra validações ✓
├─ Test 7: Histórico registra edições ✓
├─ Test 8: Envio usa dados corretos ✓
└─ Test 9: Status GAL atualizado ✓

teste_integracao_todas_fases.py:
├─ Test 1: Fase 1 → Fase 2 ✓
├─ Test 2: Fase 2 → Fase 3 ✓
├─ Test 3: Fase 3 → Fase 4 ✓
├─ Test 4: Fase 4 → Envio ✓
├─ Test 5: Dados fluem corretamente ✓
└─ Test 6: Sem perda de dados ✓
```

### ✅ CRITÉRIO DE ACEITAÇÃO FASE 4

```
✅ Todas fases integradas
✅ Fluxo completo E2E funciona
✅ Histórico registra equipamento
✅ Histórico registra validações
✅ Histórico registra edições
✅ Envio usa dados corretos
✅ Status GAL atualizado
✅ Sistema é 100% auditável
✅ Todos testes passando
```

---

## 🔵 FASE 5: REFINAMENTO (Semana 5-6)

### 📌 OBJETIVO
Otimização, testes extensivos, documentação e preparação para produção

### 📦 COMPONENTES

#### **5.1 - Testes Extensivos**
```
teste_performance.py:
├─ Test 1: Detecção equip < 500ms ✓
├─ Test 2: Análise < 2s ✓
├─ Test 3: Edição responsiva < 100ms ✓
├─ Test 4: Envio < 5s ✓
└─ Test 5: Histórico < 100ms ✓

teste_stress.py:
├─ Test 1: 100 análises simultâneas ✓
├─ Test 2: Arquivo grande (1000 amostras) ✓
├─ Test 3: Múltiplos equipamentos ✓
└─ Test 4: Edições massivas ✓

teste_regressao.py:
├─ Test 1: VR1e2 ainda funciona ✓
├─ Test 2: ZDC ainda funciona ✓
├─ Test 3: Análises antigas compatíveis ✓
└─ Test 4: Histórico antigo intacto ✓

teste_usuarios_reais.py (Beta Testing):
├─ Test 1: 3 usuários com 7500 ✓
├─ Test 2: 2 usuários com CFX96 ✓
├─ Test 3: 1 usuário com QuantStudio ✓
└─ Test 4: Coexistência sem conflitos ✓
```

#### **5.2 - Otimizações**
```
CACHE:
├─ EquipmentRegistry: cache em memória
├─ ExamRegistry: recarrega ao salvar novo
├─ Padrões de equipamento: cache em disco
└─ Resultado de análise: cache 15 min

PERFORMANCE:
├─ Lazy loading de extractores
├─ Parallelização de fórmulas
├─ Índices em histórico_analises.csv
└─ Async para envio GAL

SEGURANÇA:
├─ Validação de entrada em todas funções
├─ Sanitização de fórmulas
├─ Auditoria de mudanças
└─ Backup automático antes envio
```

#### **5.3 - Documentação Completa**
```
DOCUMENTAÇÃO GERADA:

1. MANUAL DO USUÁRIO
   ├─ Como usar mapeamento automático
   ├─ Como editar resultados
   ├─ Como enviar para GAL
   └─ Troubleshooting comum

2. GUIA TÉCNICO
   ├─ Arquitetura das 5 fases
   ├─ Fluxo de dados
   ├─ Equipment Registry
   ├─ Formula Parser
   ├─ Rules Engine
   └─ APIs internas

3. GUIA DE ADMINSTRAÇÃO
   ├─ Como cadastrar novo equipamento
   ├─ Como adicionar novo exame
   ├─ Como customizar fórmulas/regras
   └─ Troubleshooting de produção

4. CHANGELOG
   ├─ Fase 1: Auto-detecção + Registry
   ├─ Fase 2: Parser + Rules
   ├─ Fase 3: Resultado editável
   ├─ Fase 4: Integração completa
   └─ Fase 5: Refinamento

5. API REFERENCE
   ├─ Todas classes/funções públicas
   ├─ Parâmetros e retornos
   ├─ Exemplos de uso
   └─ Erros comuns
```

#### **5.4 - Treinamento**
```
MATERIAIS DE TREINAMENTO:

1. VIDEO TUTORIAIS
   ├─ 5 min: Novo fluxo de análise
   ├─ 10 min: Edição de resultados
   ├─ 5 min: Envio ao GAL
   └─ 10 min: Troubleshooting

2. WORKSHOP
   ├─ Demo com dados reais
   ├─ Hands-on: cada usuário faz 1 análise
   ├─ Q&A
   └─ Feedback

3. DOCUMENTAÇÃO ONLINE
   ├─ Wiki com todos detalhes
   ├─ FAQ atualizado
   ├─ Exemplos de configuração
   └─ Links para suporte
```

### ✅ CRITÉRIO DE ACEITAÇÃO FASE 5

```
✅ Todos testes passando (performance, stress, regressão)
✅ Performance dentro dos limites
✅ Beta testing com usuários reais OK
✅ Documentação completa
✅ Treinamento realizado
✅ Plano de rollback definido
✅ Monitoramento em produção pronto
✅ Support team treinado
✅ Pronto para produção
```

---

## 📊 RESUMO EXECUTIVO

### CRONOGRAMA TOTAL

```
SEMANA 1-2: FASE 1 (Foundation)
├─ Detector de equipamento
├─ Equipment Registry
└─ Extractores específicos
└─ Resultado: Auto-detecção + extração normalizada

SEMANA 2-3: FASE 2 (Analysis)
├─ Formula Parser
├─ Rules Engine
└─ Integração com UniversalEngine
└─ Resultado: Análise com fórmulas/regras dinâmicas

SEMANA 3-4: FASE 3 (Results)
├─ Tela gráfica de resultados
├─ Editor de resultados
└─ ResultadoManager
└─ Resultado: User vê e edita antes de enviar

SEMANA 4-5: FASE 4 (Integration)
├─ Atualizar histórico
├─ Atualizar envio GAL
└─ Fluxo completo E2E
└─ Resultado: Sistema 100% integrado e auditável

SEMANA 5-6: FASE 5 (Refinement)
├─ Testes extensivos
├─ Otimizações
├─ Documentação
└─ Treinamento
└─ Resultado: Pronto para produção

TOTAL: ~6 semanas para implementação completa
```

### RISCOS E MITIGAÇÕES

```
RISCO 1: Complexidade de fórmulas muito alta
└─ Mitigação: Suportar apenas operadores simples inicialmente
└─ Upgrade: Adicionar operadores complexos depois

RISCO 2: Performance degradada com muitas regras
└─ Mitigação: Cachear resultados de fórmulas
└─ Upgrade: Parallelizar avaliação

RISCO 3: User acha edição confusa
└─ Mitigação: Interface muito simples, intuitive
└─ Upgrade: Validação em tempo real, avisos claros

RISCO 4: Histórico fica muito grande
└─ Mitigação: Arquivar dados antigos mensalmente
└─ Upgrade: Migrar para SQLite depois

RISCO 5: Equipamento novo não detectado
└─ Mitigação: Fallback para manual + formulário de novo equip
└─ Upgrade: User pode auto-registrar padrão
```

### MÉTRICAS DE SUCESSO

```
✅ Detecção automática: 95%+ acurácia
✅ Tempo de análise: < 2 segundos
✅ Taxa de erro de fórmulas: < 0.1%
✅ User satisfaction: > 4.5/5 stars
✅ Tempo de envio GAL: < 5 segundos
✅ Taxa de sucesso envio: > 99%
✅ Zero data loss
✅ Auditoria 100% completa
```

---

## 🚀 PRÓXIMOS PASSOS

1. ✅ **Aprovação do plano** ← Você está aqui
2. ⏳ **Início Fase 1** (Auto-detecção + Registry)
3. ⏳ **Review ao final de cada fase**
4. ⏳ **Testes beta com usuários**
5. ⏳ **Rollout para produção**

---

**Data:** 2025-12-07  
**Duração:** 6 semanas  
**Status:** Pronto para implementação  
**Próximo:** Aprovação + Início Fase 1
