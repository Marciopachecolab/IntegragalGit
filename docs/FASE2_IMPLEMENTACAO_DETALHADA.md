# 🔵 FASE 2 - IMPLEMENTAÇÃO DETALHADA
## Parser de Fórmulas + Rules Engine

**Data início:** 08/12/2025  
**Duração estimada:** 1-2 semanas  
**Status:** ✅ Fase 1 concluída - Pronto para iniciar

---

## 📋 PRÉ-REQUISITOS (CHECKLIST)

Antes de iniciar a Fase 2, verificar:

- [x] **Fase 1 concluída e testada**
  - [x] Equipment Detector funcionando (42 testes passando)
  - [x] Equipment Registry carregando configs
  - [x] Extractors normalizando dados
  - [x] Taxa de sucesso: 91% (42/46 testes)

- [ ] **Ambiente preparado**
  - [ ] Python 3.13+ instalado
  - [ ] Dependências atualizadas (requirements.txt)
  - [ ] UTF-8 sem BOM em todos arquivos
  - [ ] pytest configurado

- [ ] **Conhecimento técnico**
  - [ ] Entendimento de AST (Abstract Syntax Tree) Python
  - [ ] Segurança em eval() - boas práticas
  - [ ] Padrão de Rules Engine
  - [ ] Dataclasses Python

---

## 🎯 OBJETIVOS DA FASE 2

1. ✅ **Criar Formula Parser seguro** para avaliar expressões matemáticas/lógicas
2. ✅ **Criar Rules Engine** para aplicar regras customizadas
3. ✅ **Integrar com UniversalEngine** para análise completa
4. ✅ **Garantir segurança** (sem injeção de código)
5. ✅ **Criar testes abrangentes** (cobertura >90%)

---

## 📦 ESTRUTURA DE ARQUIVOS A CRIAR

```
integragal/
├── services/
│   ├── formula_parser.py          ← NOVO (Etapa 2.1)
│   ├── rules_engine.py             ← NOVO (Etapa 2.2)
│   └── universal_engine.py         ← ATUALIZAR (Etapa 2.3)
│
├── tests/
│   ├── test_formula_parser.py      ← NOVO (Etapa 2.4)
│   ├── test_rules_engine.py        ← NOVO (Etapa 2.5)
│   └── test_universal_integration.py ← NOVO (Etapa 2.6)
│
└── docs/
    ├── FASE2_FORMULA_PARSER.md     ← Documentação técnica
    ├── FASE2_RULES_ENGINE.md       ← Documentação técnica
    └── FASE2_CONCLUIDA.md          ← Relatório final
```

---

## 🔧 ETAPA 2.1 - FORMULA PARSER

### 📝 Descrição
Criar parser seguro para avaliar expressões matemáticas e lógicas com variáveis dinâmicas.

### 🎯 Objetivos
- Avaliar fórmulas como: `(CT_DEN1 + CT_DEN2) / 2 < 33`
- Substituir variáveis por valores reais
- Garantir segurança (whitelist de operadores)
- Tratamento robusto de erros

### 📋 Tarefas

#### **2.1.1 - Estrutura base e dataclasses**
```python
# services/formula_parser.py

@dataclass
class FormulaValidationResult:
    """Resultado da validação de uma fórmula"""
    valida: bool
    mensagem: str
    variaveis_encontradas: List[str]
    operadores_encontrados: List[str]

@dataclass
class FormulaEvaluationResult:
    """Resultado da avaliação de uma fórmula"""
    sucesso: bool
    resultado: Union[bool, float, str, None]
    mensagem_erro: Optional[str]
    tempo_execucao_ms: float
    variaveis_usadas: Dict[str, Any]
```

**✅ Checklist:**
- [ ] Criar arquivo `services/formula_parser.py`
- [ ] Importar bibliotecas: `ast`, `re`, `typing`, `dataclasses`, `logging`
- [ ] Definir dataclasses `FormulaValidationResult` e `FormulaEvaluationResult`
- [ ] Adicionar docstrings completas

---

#### **2.1.2 - Whitelist de segurança**
```python
# Operadores permitidos (WHITELIST)
OPERADORES_PERMITIDOS = {
    # Matemáticos
    'Add': '+',      # Adição
    'Sub': '-',      # Subtração
    'Mult': '*',     # Multiplicação
    'Div': '/',      # Divisão
    'Mod': '%',      # Módulo
    'Pow': '**',     # Potência
    
    # Comparação
    'Eq': '==',      # Igual
    'NotEq': '!=',   # Diferente
    'Lt': '<',       # Menor
    'LtE': '<=',     # Menor ou igual
    'Gt': '>',       # Maior
    'GtE': '>=',     # Maior ou igual
    
    # Lógicos
    'And': 'and',    # E lógico
    'Or': 'or',      # OU lógico
    'Not': 'not',    # NÃO lógico
}

NODES_PERMITIDOS = {
    ast.Expression,
    ast.BinOp,        # Operação binária (a + b)
    ast.UnaryOp,      # Operação unária (-a)
    ast.Compare,      # Comparação (a < b)
    ast.BoolOp,       # Operação booleana (a and b)
    ast.Name,         # Nome de variável
    ast.Constant,     # Constante (número, string)
    ast.Num,          # Número (Python < 3.8)
    ast.Str,          # String (Python < 3.8)
}

# Padrão de variáveis permitidas
PATTERN_VARIAVEL = re.compile(r'^(CT_|resultado_|flag_|controle_)[A-Z0-9_]+$', re.IGNORECASE)
```

**✅ Checklist:**
- [ ] Definir `OPERADORES_PERMITIDOS` (dicionário completo)
- [ ] Definir `NODES_PERMITIDOS` (tipos AST permitidos)
- [ ] Definir `PATTERN_VARIAVEL` (regex para validação)
- [ ] Adicionar comentários explicativos

---

#### **2.1.3 - Função de validação de fórmula**
```python
def validar_formula(expressao: str) -> FormulaValidationResult:
    """
    Valida uma fórmula antes de avaliar.
    
    Verifica:
    - Sintaxe válida
    - Apenas operadores permitidos
    - Variáveis com padrão correto
    - Sem funções perigosas (__import__, eval, etc)
    
    Args:
        expressao: String com a fórmula (ex: "CT_DEN1 < 30")
        
    Returns:
        FormulaValidationResult com status e detalhes
    """
    # 1. Verificar string vazia
    # 2. Tentar parsear com ast.parse()
    # 3. Verificar nodes do AST
    # 4. Validar operadores
    # 5. Extrair e validar variáveis
    # 6. Retornar resultado
```

**✅ Checklist:**
- [ ] Implementar `validar_formula()`
- [ ] Tratar string vazia
- [ ] Usar `ast.parse()` para análise sintática
- [ ] Percorrer AST validando cada node
- [ ] Extrair variáveis com regex
- [ ] Retornar `FormulaValidationResult` completo
- [ ] Adicionar logging para cada validação

---

#### **2.1.4 - Função de avaliação segura**
```python
def avaliar_formula(
    expressao: str, 
    variaveis: Dict[str, Any],
    timeout_segundos: float = 1.0
) -> FormulaEvaluationResult:
    """
    Avalia uma fórmula com segurança.
    
    Processo:
    1. Valida fórmula
    2. Substitui variáveis
    3. Avalia com eval() controlado
    4. Retorna resultado
    
    Args:
        expressao: Fórmula (ex: "(CT_DEN1 + CT_DEN2) / 2 < 33")
        variaveis: Dict com valores (ex: {"CT_DEN1": 15.5, "CT_DEN2": 18.2})
        timeout_segundos: Tempo máximo de execução
        
    Returns:
        FormulaEvaluationResult com resultado ou erro
    """
    # 1. Validar fórmula
    # 2. Verificar variáveis disponíveis
    # 3. Preparar contexto seguro (__builtins__={})
    # 4. Avaliar com timeout
    # 5. Capturar exceções
    # 6. Retornar resultado
```

**✅ Checklist:**
- [ ] Implementar `avaliar_formula()`
- [ ] Chamar `validar_formula()` primeiro
- [ ] Verificar variáveis disponíveis no dict
- [ ] Criar contexto seguro (`__builtins__={}`)
- [ ] Usar `eval()` com contexto restrito
- [ ] Implementar timeout (threading ou signal)
- [ ] Capturar `SyntaxError`, `NameError`, `ZeroDivisionError`, etc
- [ ] Medir tempo de execução
- [ ] Retornar `FormulaEvaluationResult` completo

---

#### **2.1.5 - Funções auxiliares**
```python
def extrair_variaveis(expressao: str) -> List[str]:
    """Extrai nomes de variáveis de uma fórmula"""
    # Usar regex PATTERN_VARIAVEL
    pass

def substituir_variaveis(expressao: str, variaveis: Dict[str, Any]) -> str:
    """Substitui variáveis por valores na fórmula"""
    # Substituir cada variável encontrada
    pass

def formatar_erro(exception: Exception) -> str:
    """Formata mensagem de erro amigável"""
    # Converter exceção técnica em mensagem clara
    pass
```

**✅ Checklist:**
- [ ] Implementar `extrair_variaveis()`
- [ ] Implementar `substituir_variaveis()`
- [ ] Implementar `formatar_erro()`
- [ ] Adicionar testes unitários para cada uma

---

### 📊 Critérios de Aceitação - Etapa 2.1

```
✅ Arquivo formula_parser.py criado (~250-350 linhas)
✅ Dataclasses definidas corretamente
✅ Whitelist de segurança implementada
✅ validar_formula() funciona corretamente
✅ avaliar_formula() avalia expressões com segurança
✅ Timeout implementado e funciona
✅ Tratamento de erros robusto
✅ Logging em todas operações críticas
✅ Código UTF-8 sem BOM
✅ Docstrings completas
```

---

### 🎯 PROMPT PARA ETAPA 2.1

```
Implementar Formula Parser (Etapa 2.1 da Fase 2):

CONTEXTO:
- Fase 1 concluída (42 testes passando)
- Precisamos avaliar fórmulas como: "(CT_DEN1 + CT_DEN2) / 2 < 33"
- Segurança é CRÍTICA (sem injeção de código)

TAREFAS:
1. Criar services/formula_parser.py
2. Implementar dataclasses:
   - FormulaValidationResult
   - FormulaEvaluationResult
3. Definir whitelist de segurança:
   - OPERADORES_PERMITIDOS (matemáticos, comparação, lógicos)
   - NODES_PERMITIDOS (tipos AST)
   - PATTERN_VARIAVEL (regex para CT_*, resultado_*, flag_*)
4. Implementar validar_formula(expressao: str):
   - Parsear com ast.parse()
   - Validar nodes do AST
   - Verificar operadores
   - Extrair e validar variáveis
5. Implementar avaliar_formula(expressao, variaveis, timeout):
   - Validar primeiro
   - Substituir variáveis
   - Avaliar com eval() seguro (__builtins__={})
   - Timeout de 1 segundo
   - Tratamento robusto de erros
6. Implementar funções auxiliares:
   - extrair_variaveis()
   - substituir_variaveis()
   - formatar_erro()

EXEMPLOS DE FÓRMULAS:
- "(CT_DEN1 + CT_DEN2) / 2 < 33" → true/false
- "CT_ZIKA < 30 and CT_DENGUE > 15" → true/false
- "resultado_SC2 == 'Detectado'" → true/false

SEGURANÇA:
- Whitelist estrita de operadores
- Sem __import__, eval, exec, open, etc
- Timeout obrigatório
- Contexto isolado (__builtins__={})

REQUISITOS:
- UTF-8 sem BOM
- Logging em operações críticas
- Docstrings completas
- Type hints em tudo
- ~250-350 linhas

CRITÉRIOS:
✅ validar_formula() detecta fórmulas inválidas
✅ avaliar_formula() avalia corretamente
✅ Timeout funciona
✅ Segurança validada (rejeita __import__, etc)
✅ Tratamento de erros robusto

Prossiga com a implementação seguindo as tarefas 2.1.1 a 2.1.5.
```

---

## 🔧 ETAPA 2.2 - RULES ENGINE

### 📝 Descrição
Criar engine de regras para aplicar lógica condicional complexa aos resultados de análise.

### 🎯 Objetivos
- Interpretar regras customizadas (JSON)
- Aplicar validações condicionais
- Gerar relatório de validações
- Integrar com Formula Parser

### 📋 Tarefas

#### **2.2.1 - Estrutura base e dataclasses**
```python
# services/rules_engine.py

@dataclass
class Validacao:
    """Resultado de uma validação individual"""
    regra_id: str
    regra_nome: str
    resultado: str  # "passou", "falhou", "aviso", "não_aplicavel"
    detalhes: str
    impacto: str  # "critico", "alto", "medio", "baixo"
    timestamp: datetime

@dataclass
class RulesResult:
    """Resultado completo da aplicação de regras"""
    status: str  # "valida", "invalida", "aviso"
    validacoes: List[Validacao]
    mensagens_erro: List[str]
    mensagens_aviso: List[str]
    detalhes: str
    tempo_execucao_ms: float
```

**✅ Checklist:**
- [ ] Criar arquivo `services/rules_engine.py`
- [ ] Importar bibliotecas necessárias
- [ ] Definir dataclasses `Validacao` e `RulesResult`
- [ ] Adicionar docstrings

---

#### **2.2.2 - Tipos de regras suportadas**
```python
# Tipos de regras
TIPO_REGRA = {
    'booleana': 'Regra simples true/false',
    'condicional': 'Regra if-then',
    'sequencia': 'Alvos obrigatórios',
    'exclusao_mutua': 'Apenas um pode ser positivo',
    'formula': 'Avaliação de fórmula',
    'threshold': 'Valor dentro de range',
}

# Exemplo de estrutura de regras
EXEMPLO_REGRAS = {
    "requer_dois_alvos": True,  # Booleana simples
    "formulas": [
        "(CT_DEN1 + CT_DEN2) / 2 < 33"
    ],
    "condicoes": [
        {
            "tipo": "condicional",
            "descricao": "DEN1 positivo requer DEN2 positivo",
            "if": "resultado_DEN1 == 'Detectado'",
            "then": "resultado_DEN2 == 'Detectado'",
            "impacto": "alto"
        }
    ],
    "sequencia": {
        "alvos_obrigatorios": ["DEN1", "DEN2"],
        "descricao": "Ambos alvos devem estar presentes"
    }
}
```

**✅ Checklist:**
- [ ] Definir `TIPO_REGRA` (enumeração)
- [ ] Documentar estrutura JSON de cada tipo
- [ ] Criar exemplos de regras
- [ ] Adicionar validação de estrutura

---

#### **2.2.3 - Aplicador de regras**
```python
def aplicar_regras(
    regras_dict: Dict[str, Any],
    resultados_dict: Dict[str, Any],
    formula_parser: Optional[Any] = None
) -> RulesResult:
    """
    Aplica todas as regras aos resultados.
    
    Processo:
    1. Valida estrutura de regras
    2. Aplica cada tipo de regra
    3. Coleta resultados
    4. Gera status geral
    
    Args:
        regras_dict: Dict com todas regras
        resultados_dict: Dict com resultados da análise
        formula_parser: Instância do parser (injetado)
        
    Returns:
        RulesResult com status completo
    """
    # 1. Validar estrutura
    # 2. Aplicar regras booleanas
    # 3. Aplicar fórmulas
    # 4. Aplicar condicionais
    # 5. Aplicar sequência
    # 6. Aplicar exclusão mútua
    # 7. Gerar status geral
    # 8. Retornar resultado
```

**✅ Checklist:**
- [ ] Implementar `aplicar_regras()`
- [ ] Validar estrutura de entrada
- [ ] Implementar aplicador para cada tipo de regra
- [ ] Coletar validações em lista
- [ ] Determinar status geral (válida/inválida/aviso)
- [ ] Medir tempo de execução
- [ ] Retornar `RulesResult` completo

---

#### **2.2.4 - Aplicadores específicos por tipo**
```python
def aplicar_regra_booleana(
    nome: str, 
    valor: bool, 
    resultados: Dict
) -> Validacao:
    """Aplica regra booleana simples"""
    pass

def aplicar_regra_formula(
    formula: str,
    resultados: Dict,
    parser: Any
) -> Validacao:
    """Aplica regra baseada em fórmula"""
    pass

def aplicar_regra_condicional(
    regra: Dict,
    resultados: Dict,
    parser: Any
) -> Validacao:
    """Aplica regra if-then"""
    pass

def aplicar_regra_sequencia(
    regra: Dict,
    resultados: Dict
) -> Validacao:
    """Valida presença de alvos obrigatórios"""
    pass

def aplicar_regra_exclusao_mutua(
    regra: Dict,
    resultados: Dict
) -> Validacao:
    """Valida exclusão mútua entre alvos"""
    pass
```

**✅ Checklist:**
- [ ] Implementar cada função aplicadora
- [ ] Tratar casos especiais (dados faltantes)
- [ ] Retornar `Validacao` com detalhes completos
- [ ] Adicionar logging

---

#### **2.2.5 - Gerador de status geral**
```python
def determinar_status_geral(validacoes: List[Validacao]) -> str:
    """
    Determina status geral baseado em todas validações.
    
    Regras:
    - Se alguma crítica falhou → "invalida"
    - Se todas passaram → "valida"
    - Se há avisos mas nenhuma falha → "aviso"
    
    Args:
        validacoes: Lista de validações aplicadas
        
    Returns:
        Status: "valida", "invalida", "aviso"
    """
    pass

def gerar_mensagens(validacoes: List[Validacao]) -> Tuple[List[str], List[str]]:
    """Gera mensagens de erro e aviso"""
    pass

def gerar_detalhes_resumo(validacoes: List[Validacao]) -> str:
    """Gera resumo textual das validações"""
    pass
```

**✅ Checklist:**
- [ ] Implementar `determinar_status_geral()`
- [ ] Implementar `gerar_mensagens()`
- [ ] Implementar `gerar_detalhes_resumo()`
- [ ] Considerar severidade/impacto das validações

---

### 📊 Critérios de Aceitação - Etapa 2.2

```
✅ Arquivo rules_engine.py criado (~300-400 linhas)
✅ Dataclasses Validacao e RulesResult definidas
✅ aplicar_regras() funciona corretamente
✅ Todos tipos de regras suportados:
   - Booleana
   - Fórmula
   - Condicional
   - Sequência
   - Exclusão mútua
✅ Status geral determinado corretamente
✅ Mensagens claras e detalhadas
✅ Integração com Formula Parser
✅ Logging completo
✅ Código UTF-8 sem BOM
✅ Docstrings completas
```

---

### 🎯 PROMPT PARA ETAPA 2.2

```
Implementar Rules Engine (Etapa 2.2 da Fase 2):

CONTEXTO:
- Formula Parser já implementado (Etapa 2.1)
- Precisamos aplicar regras complexas aos resultados
- Exemplo: "Se DEN1 positivo, DEN2 deve ser positivo"

TAREFAS:
1. Criar services/rules_engine.py
2. Implementar dataclasses:
   - Validacao (resultado individual)
   - RulesResult (resultado completo)
3. Definir tipos de regras suportadas:
   - Booleana: "requer_dois_alvos": true
   - Fórmula: "(CT_DEN1 + CT_DEN2) / 2 < 33"
   - Condicional: if-then
   - Sequência: alvos obrigatórios
   - Exclusão mútua: apenas um positivo
4. Implementar aplicar_regras(regras_dict, resultados_dict):
   - Validar estrutura de entrada
   - Aplicar cada tipo de regra
   - Coletar validações
   - Determinar status geral
5. Implementar aplicadores específicos:
   - aplicar_regra_booleana()
   - aplicar_regra_formula()
   - aplicar_regra_condicional()
   - aplicar_regra_sequencia()
   - aplicar_regra_exclusao_mutua()
6. Implementar gerador de status:
   - determinar_status_geral()
   - gerar_mensagens()
   - gerar_detalhes_resumo()

INTEGRAÇÃO:
- Usar formula_parser.avaliar_formula() para regras de fórmula
- Injeção de dependência (passar parser como parâmetro)

ESTRUTURA DE ENTRADA:
regras_dict = {
    "requer_dois_alvos": True,
    "formulas": ["(CT_DEN1 + CT_DEN2) / 2 < 33"],
    "condicoes": [{
        "if": "resultado_DEN1 == 'Detectado'",
        "then": "resultado_DEN2 == 'Detectado'"
    }]
}

resultados_dict = {
    "alvo_DEN1": {"resultado": "Detectado", "ct": 15.5},
    "alvo_DEN2": {"resultado": "Detectado", "ct": 18.2}
}

ESTRUTURA DE SAÍDA:
RulesResult(
    status="valida",
    validacoes=[...],
    mensagens_erro=[],
    mensagens_aviso=[],
    detalhes="Todas validações passaram"
)

REQUISITOS:
- UTF-8 sem BOM
- Logging completo
- Docstrings em tudo
- Type hints
- ~300-400 linhas

CRITÉRIOS:
✅ Todos tipos de regras funcionam
✅ Status geral correto
✅ Mensagens claras
✅ Integração com Parser OK

Prossiga com implementação seguindo tarefas 2.2.1 a 2.2.5.
```

---

## 🔧 ETAPA 2.3 - INTEGRAÇÃO COM UNIVERSAL ENGINE

### 📝 Descrição
Integrar Formula Parser e Rules Engine ao motor de análise existente.

### 🎯 Objetivos
- Adicionar avaliação de fórmulas ao fluxo
- Adicionar aplicação de regras ao fluxo
- Estender resultado com validações
- Manter compatibilidade com código existente

### 📋 Tarefas

#### **2.3.1 - Atualizar imports e dependências**
```python
# services/universal_engine.py

# Novos imports
from services.formula_parser import (
    avaliar_formula,
    validar_formula,
    FormulaEvaluationResult
)
from services.rules_engine import (
    aplicar_regras,
    RulesResult,
    Validacao
)
```

**✅ Checklist:**
- [ ] Adicionar imports do formula_parser
- [ ] Adicionar imports do rules_engine
- [ ] Verificar dependências circulares

---

#### **2.3.2 - Estender dataclass de resultado**
```python
@dataclass
class AnaliseResultado:
    """Resultado completo da análise (ESTENDIDO)"""
    # Campos existentes
    status: str
    alvos: Dict[str, Any]
    controles: Dict[str, Any]
    
    # NOVOS campos (Fase 2)
    validacoes_aplicadas: List[Validacao] = field(default_factory=list)
    formulas_avaliadas: List[Dict[str, Any]] = field(default_factory=list)
    rules_result: Optional[RulesResult] = None
    status_geral: str = "pendente"  # "valida", "invalida", "aviso"
    pronto_para_envio_gal: bool = False
```

**✅ Checklist:**
- [ ] Adicionar campos novos ao AnaliseResultado
- [ ] Manter campos existentes intactos
- [ ] Adicionar defaults apropriados
- [ ] Atualizar docstring

---

#### **2.3.3 - Atualizar método processar_exame()**
```python
def processar_exame(
    df: pd.DataFrame,
    config_exame: ExamConfig,
    metadata: Dict[str, Any]
) -> AnaliseResultado:
    """
    Processa exame completo (ATUALIZADO FASE 2).
    
    Novo fluxo:
    1. Análise CT básica (existente)
    2. NOVO: Avaliar fórmulas
    3. NOVO: Aplicar rules engine
    4. NOVO: Determinar status final
    5. Retornar resultado completo
    """
    # FASE 1: CT Logic (existente)
    alvos = _processar_alvos_ct(df, config_exame)
    controles = _processar_controles(df, config_exame)
    
    # FASE 2: Fórmulas (NOVO)
    formulas_resultado = []
    if hasattr(config_exame, 'formulas') and config_exame.formulas:
        formulas_resultado = _avaliar_formulas(
            config_exame.formulas,
            alvos,
            controles
        )
    
    # FASE 2: Rules Engine (NOVO)
    rules_result = None
    if hasattr(config_exame, 'regras_extra') and config_exame.regras_extra:
        rules_result = aplicar_regras(
            config_exame.regras_extra,
            {'alvos': alvos, 'controles': controles}
        )
    
    # FASE 2: Status Final (NOVO)
    status_geral = _determinar_status_final(
        alvos,
        controles,
        formulas_resultado,
        rules_result
    )
    
    pronto_envio = (status_geral == "valida")
    
    # Retornar resultado completo
    return AnaliseResultado(
        status=status_geral,
        alvos=alvos,
        controles=controles,
        validacoes_aplicadas=rules_result.validacoes if rules_result else [],
        formulas_avaliadas=formulas_resultado,
        rules_result=rules_result,
        status_geral=status_geral,
        pronto_para_envio_gal=pronto_envio
    )
```

**✅ Checklist:**
- [ ] Manter lógica CT existente
- [ ] Adicionar avaliação de fórmulas
- [ ] Adicionar aplicação de regras
- [ ] Determinar status final combinando tudo
- [ ] Retornar resultado estendido
- [ ] Manter compatibilidade com código existente

---

#### **2.3.4 - Implementar funções auxiliares**
```python
def _avaliar_formulas(
    formulas: List[str],
    alvos: Dict,
    controles: Dict
) -> List[Dict[str, Any]]:
    """Avalia lista de fórmulas"""
    # Preparar variáveis (CT_*, resultado_*)
    # Avaliar cada fórmula
    # Retornar lista de resultados
    pass

def _determinar_status_final(
    alvos: Dict,
    controles: Dict,
    formulas: List,
    rules: Optional[RulesResult]
) -> str:
    """Determina status final combinando tudo"""
    # CT básico OK?
    # Controles OK?
    # Fórmulas passaram?
    # Regras passaram?
    # Retornar: "valida", "invalida", "aviso"
    pass

def _preparar_variaveis_formulas(
    alvos: Dict,
    controles: Dict
) -> Dict[str, Any]:
    """Prepara dict de variáveis para fórmulas"""
    # CT_DEN1 = alvos['DEN1']['ct']
    # resultado_DEN1 = alvos['DEN1']['resultado']
    # Retornar dict completo
    pass
```

**✅ Checklist:**
- [ ] Implementar `_avaliar_formulas()`
- [ ] Implementar `_determinar_status_final()`
- [ ] Implementar `_preparar_variaveis_formulas()`
- [ ] Adicionar logging em cada função
- [ ] Tratar casos especiais (dados faltantes)

---

### 📊 Critérios de Aceitação - Etapa 2.3

```
✅ universal_engine.py atualizado
✅ AnaliseResultado estendido com novos campos
✅ processar_exame() integra parser + rules
✅ Fórmulas avaliadas corretamente
✅ Regras aplicadas corretamente
✅ Status final determinado corretamente
✅ Compatibilidade mantida com código existente
✅ Resultado pronto para Fase 3 (janela gráfica)
✅ Logging completo do fluxo
✅ Sem quebrar testes existentes
```

---

### 🎯 PROMPT PARA ETAPA 2.3

```
Integrar Formula Parser + Rules Engine ao Universal Engine (Etapa 2.3 da Fase 2):

CONTEXTO:
- Formula Parser implementado (Etapa 2.1)
- Rules Engine implementado (Etapa 2.2)
- Precisamos integrar ao motor de análise existente

TAREFAS:
1. Atualizar services/universal_engine.py:
   - Adicionar imports (formula_parser, rules_engine)
   - Estender dataclass AnaliseResultado com:
     * validacoes_aplicadas: List[Validacao]
     * formulas_avaliadas: List[Dict]
     * rules_result: Optional[RulesResult]
     * status_geral: str
     * pronto_para_envio_gal: bool

2. Atualizar método processar_exame():
   - Manter CT logic existente (Fase 1)
   - Adicionar avaliação de fórmulas:
     * config_exame.formulas → avaliar cada uma
   - Adicionar aplicação de regras:
     * config_exame.regras_extra → aplicar_regras()
   - Determinar status final:
     * Combinar: CT + fórmulas + regras
     * Retornar: "valida", "invalida", "aviso"

3. Implementar funções auxiliares:
   - _avaliar_formulas(formulas, alvos, controles)
   - _determinar_status_final(alvos, controles, formulas, rules)
   - _preparar_variaveis_formulas(alvos, controles)

4. Manter compatibilidade:
   - Campos novos são opcionais
   - Código existente não quebra
   - Testes existentes continuam passando

FLUXO ATUALIZADO:
processar_exame():
├─ 1. CT Logic básico (existente)
├─ 2. Avaliar fórmulas (NOVO)
│  └─ Para cada fórmula em config_exame.formulas:
│     └─ avaliar_formula(expressao, variaveis)
├─ 3. Aplicar regras (NOVO)
│  └─ aplicar_regras(config_exame.regras_extra, resultados)
├─ 4. Status final (NOVO)
│  └─ Combinar: CT OK? + Fórmulas OK? + Regras OK?
└─ 5. Retornar AnaliseResultado estendido

EXEMPLO DE CONFIG EXAME (atualizado):
{
    "nome": "MPX Kit ABC",
    "alvos": [...],  # existente
    "controles": [...],  # existente
    "formulas": [  # NOVO
        "(CT_DEN1 + CT_DEN2) / 2 < 33"
    ],
    "regras_extra": {  # NOVO
        "requer_dois_alvos": True,
        "condicoes": [...]
    }
}

REQUISITOS:
- Manter código existente funcionando
- UTF-8 sem BOM
- Logging do novo fluxo
- Docstrings atualizadas
- Type hints

CRITÉRIOS:
✅ Integração funciona end-to-end
✅ Fórmulas avaliadas corretamente
✅ Regras aplicadas corretamente
✅ Status final correto
✅ Resultado pronto para Fase 3
✅ Testes existentes ainda passam

Prossiga com implementação seguindo tarefas 2.3.1 a 2.3.4.
```

---

## 🧪 ETAPA 2.4 - TESTES FORMULA PARSER

### 📝 Descrição
Criar suite completa de testes para o Formula Parser.

### 🎯 Objetivos
- Cobertura >90%
- Testar casos válidos e inválidos
- Testar segurança
- Testar performance

### 📋 Testes a Implementar

```python
# tests/test_formula_parser.py

class TestValidarFormula:
    """Testes da função validar_formula()"""
    
    def test_formula_valida_simples(self):
        """Testa fórmula simples válida"""
        assert validar_formula("CT_DEN1 < 30").valida == True
    
    def test_formula_valida_complexa(self):
        """Testa fórmula complexa válida"""
        assert validar_formula("(CT_DEN1 + CT_DEN2) / 2 < 33").valida == True
    
    def test_formula_invalida_sintaxe(self):
        """Testa fórmula com erro de sintaxe"""
        assert validar_formula("CT_DEN1 < <").valida == False
    
    def test_formula_invalida_operador_proibido(self):
        """Testa rejeição de operador proibido"""
        assert validar_formula("__import__('os')").valida == False
    
    def test_formula_invalida_variavel_padrao(self):
        """Testa rejeição de variável fora do padrão"""
        assert validar_formula("variavel_invalida < 30").valida == False

class TestAvaliarFormula:
    """Testes da função avaliar_formula()"""
    
    def test_avaliar_aritmetica_simples(self):
        """Testa avaliação aritmética simples"""
        resultado = avaliar_formula(
            "(15.5 + 18.2) / 2 < 33",
            {"CT_DEN1": 15.5, "CT_DEN2": 18.2}
        )
        assert resultado.sucesso == True
        assert resultado.resultado == True
    
    def test_avaliar_comparacao_booleana(self):
        """Testa comparação booleana"""
        resultado = avaliar_formula(
            "CT_ZIKA < 30 and CT_DENGUE > 15",
            {"CT_ZIKA": 25, "CT_DENGUE": 20}
        )
        assert resultado.sucesso == True
        assert resultado.resultado == True
    
    def test_avaliar_variavel_faltando(self):
        """Testa erro quando variável não existe"""
        resultado = avaliar_formula(
            "CT_INEXISTENTE < 30",
            {}
        )
        assert resultado.sucesso == False
        assert "variável" in resultado.mensagem_erro.lower()
    
    def test_avaliar_divisao_por_zero(self):
        """Testa tratamento de divisão por zero"""
        resultado = avaliar_formula(
            "CT_DEN1 / 0",
            {"CT_DEN1": 15}
        )
        assert resultado.sucesso == False
    
    def test_avaliar_timeout(self):
        """Testa timeout em loop infinito"""
        # Criar fórmula que demora muito
        pytest.skip("Implementar teste de timeout")
    
    def test_avaliar_seguranca_import(self):
        """Testa segurança contra __import__"""
        resultado = avaliar_formula(
            "__import__('os').system('ls')",
            {}
        )
        assert resultado.sucesso == False

class TestExtracaoVariaveis:
    """Testes de extração de variáveis"""
    
    def test_extrair_variaveis_simples(self):
        """Testa extração de variáveis simples"""
        vars = extrair_variaveis("CT_DEN1 < 30")
        assert "CT_DEN1" in vars
    
    def test_extrair_variaveis_multiplas(self):
        """Testa extração de múltiplas variáveis"""
        vars = extrair_variaveis("CT_DEN1 + CT_DEN2 < resultado_ZIKA")
        assert len(vars) == 3

# Total: ~20-25 testes
```

**✅ Checklist:**
- [ ] Criar `tests/test_formula_parser.py`
- [ ] Implementar TestValidarFormula (6+ testes)
- [ ] Implementar TestAvaliarFormula (8+ testes)
- [ ] Implementar TestExtracaoVariaveis (3+ testes)
- [ ] Testar casos válidos
- [ ] Testar casos inválidos
- [ ] Testar segurança
- [ ] Testar performance
- [ ] Atingir cobertura >90%

---

### 🎯 PROMPT PARA ETAPA 2.4

```
Criar testes para Formula Parser (Etapa 2.4 da Fase 2):

TAREFAS:
1. Criar tests/test_formula_parser.py
2. Implementar TestValidarFormula:
   - test_formula_valida_simples
   - test_formula_valida_complexa
   - test_formula_invalida_sintaxe
   - test_formula_invalida_operador_proibido
   - test_formula_invalida_variavel_padrao
3. Implementar TestAvaliarFormula:
   - test_avaliar_aritmetica_simples
   - test_avaliar_comparacao_booleana
   - test_avaliar_variavel_faltando
   - test_avaliar_divisao_por_zero
   - test_avaliar_timeout (skip por enquanto)
   - test_avaliar_seguranca_import
4. Implementar TestExtracaoVariaveis:
   - test_extrair_variaveis_simples
   - test_extrair_variaveis_multiplas

EXEMPLOS DE CASOS:
- Válidos:
  * "CT_DEN1 < 30"
  * "(CT_DEN1 + CT_DEN2) / 2 < 33"
  * "CT_ZIKA < 30 and CT_DENGUE > 15"
- Inválidos:
  * "__import__('os')" → segurança
  * "variavel_invalida < 30" → padrão
  * "CT_DEN1 < <" → sintaxe

REQUISITOS:
- UTF-8 sem BOM
- Usar pytest
- Cobertura >90%
- ~20-25 testes mínimo

CRITÉRIOS:
✅ Todos testes passam
✅ Casos válidos funcionam
✅ Casos inválidos detectados
✅ Segurança validada
✅ Cobertura >90%

Execute: pytest tests/test_formula_parser.py -v
```

---

## 🧪 ETAPA 2.5 - TESTES RULES ENGINE

### 📝 Descrição
Criar suite completa de testes para o Rules Engine.

### 📋 Testes a Implementar

```python
# tests/test_rules_engine.py

class TestAplicarRegraBool eana:
    def test_requer_dois_alvos_passa(self):
        """Testa regra dois alvos - passa"""
    
    def test_requer_dois_alvos_falha(self):
        """Testa regra dois alvos - falha"""

class TestAplicarRegraFormula:
    def test_formula_passa(self):
        """Testa fórmula que passa"""
    
    def test_formula_falha(self):
        """Testa fórmula que falha"""

class TestAplicarRegraCondicional:
    def test_condicional_if_true_then_true(self):
        """Testa if-then ambos true"""
    
    def test_condicional_if_true_then_false(self):
        """Testa if-then falha"""

class TestAplicarRegras:
    def test_multiplas_regras(self):
        """Testa aplicação de múltiplas regras"""
    
    def test_status_geral_valida(self):
        """Testa status geral quando tudo passa"""
    
    def test_status_geral_invalida(self):
        """Testa status geral quando algo falha"""

# Total: ~15-20 testes
```

**✅ Checklist:**
- [ ] Criar `tests/test_rules_engine.py`
- [ ] Testar cada tipo de regra individualmente
- [ ] Testar aplicação de múltiplas regras
- [ ] Testar determinação de status geral
- [ ] Testar mensagens geradas
- [ ] Atingir cobertura >90%

---

### 🎯 PROMPT PARA ETAPA 2.5

```
Criar testes para Rules Engine (Etapa 2.5 da Fase 2):

Similar ao prompt 2.4, mas focado no rules_engine.py.
Implementar ~15-20 testes cobrindo todos os tipos de regras.

Execute: pytest tests/test_rules_engine.py -v
```

---

## 🧪 ETAPA 2.6 - TESTES DE INTEGRAÇÃO

### 📝 Descrição
Testar integração completa: UniversalEngine + Parser + Rules.

### 📋 Testes a Implementar

```python
# tests/test_universal_integration.py

class TestIntegracaoUniversalEngine:
    def test_fluxo_completo_com_formulas(self):
        """Testa fluxo completo incluindo fórmulas"""
    
    def test_fluxo_completo_com_regras(self):
        """Testa fluxo completo incluindo regras"""
    
    def test_resultado_contem_validacoes(self):
        """Testa que resultado contém validações"""
    
    def test_status_final_valida(self):
        """Testa determinação de status final válida"""
    
    def test_status_final_invalida(self):
        """Testa determinação de status final inválida"""

# Total: ~10-15 testes
```

**✅ Checklist:**
- [ ] Criar `tests/test_universal_integration.py`
- [ ] Testar fluxo end-to-end
- [ ] Testar com dados reais
- [ ] Testar compatibilidade com Fase 1
- [ ] Atingir cobertura >85%

---

### 🎯 PROMPT PARA ETAPA 2.6

```
Criar testes de integração (Etapa 2.6 da Fase 2):

Testar fluxo completo:
1. Dados extraídos (Fase 1)
2. Fórmulas avaliadas (Fase 2)
3. Regras aplicadas (Fase 2)
4. Status final determinado
5. Resultado completo retornado

Execute: pytest tests/test_universal_integration.py -v
```

---

## 📊 VALIDAÇÃO FINAL DA FASE 2

### Checklist Completo

```
✅ ETAPA 2.1 - Formula Parser
   [x] Arquivo criado (~250-350 linhas)
   [x] Dataclasses implementadas
   [x] Whitelist de segurança
   [x] validar_formula() funciona
   [x] avaliar_formula() funciona
   [x] Segurança validada
   [x] Timeout implementado

✅ ETAPA 2.2 - Rules Engine
   [x] Arquivo criado (~300-400 linhas)
   [x] Dataclasses implementadas
   [x] aplicar_regras() funciona
   [x] Todos tipos de regras suportados
   [x] Status geral correto
   [x] Mensagens claras

✅ ETAPA 2.3 - Integração
   [x] UniversalEngine atualizado
   [x] AnaliseResultado estendido
   [x] processar_exame() integrado
   [x] Compatibilidade mantida

✅ ETAPA 2.4 - Testes Parser
   [x] 20+ testes criados
   [x] Cobertura >90%
   [x] Todos testes passam

✅ ETAPA 2.5 - Testes Rules
   [x] 15+ testes criados
   [x] Cobertura >90%
   [x] Todos testes passam

✅ ETAPA 2.6 - Testes Integração
   [x] 10+ testes criados
   [x] Cobertura >85%
   [x] Todos testes passam

✅ DOCUMENTAÇÃO
   [x] Docstrings completas
   [x] Type hints em tudo
   [x] Exemplos de uso
   [x] README atualizado
```

---

## 🎯 PROMPT FINAL - VALIDAÇÃO FASE 2

```
Validar conclusão da Fase 2:

EXECUTAR TODOS OS TESTES:
pytest tests/test_formula_parser.py tests/test_rules_engine.py tests/test_universal_integration.py -v --cov=services --cov-report=term-missing

VERIFICAR:
1. Todos testes passam?
2. Cobertura >85% em services/?
3. Código UTF-8 sem BOM?
4. Docstrings completas?
5. Type hints em tudo?
6. Logging funcionando?

GERAR RELATÓRIO:
Criar docs/FASE2_CONCLUIDA.md com:
- Resumo do implementado
- Estatísticas de testes
- Cobertura de código
- Próximos passos (Fase 3)

CRITÉRIOS DE ACEITAÇÃO:
✅ Formula Parser funciona (20+ testes passando)
✅ Rules Engine funciona (15+ testes passando)
✅ Integração funciona (10+ testes passando)
✅ Segurança validada
✅ Performance OK
✅ Código documentado
✅ Pronto para Fase 3

Se todos critérios OK → Fase 2 concluída! 🎉
Próxima: Fase 3 - Janela Gráfica de Resultados
```

---

## 📈 PROGRESSO ESPERADO

```
Dia 1-2:   Etapa 2.1 (Formula Parser)
Dia 3-4:   Etapa 2.2 (Rules Engine)
Dia 5:     Etapa 2.3 (Integração)
Dia 6-7:   Etapas 2.4-2.6 (Testes)
Dia 8:     Validação e documentação
```

---

## 🚀 APÓS CONCLUSÃO DA FASE 2

Você estará pronto para:
- **Fase 3:** Criar janela gráfica de resultados editáveis
- Ver validações aplicadas na interface
- Permitir usuário editar resultados
- Re-validar após edições
- Preparar para envio GAL

---

**Documento criado:** 08/12/2025  
**Versão:** 1.0  
**Status:** Pronto para execução  
**Próximo passo:** Executar Etapa 2.1
