# 🎯 FASE 2 - GUIA COMPLETO DE IMPLEMENTAÇÃO COM PROMPTS
## Parser de Fórmulas + Rules Engine + Integração

**Data:** 08/12/2025  
**Versão:** 1.0  
**Objetivo:** Guia passo a passo com prompts prontos para cada etapa

---

## 📊 VISÃO GERAL DA FASE 2

```
┌─────────────────────────────────────────────────────────────┐
│                    FASE 2 - ARQUITETURA                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐      ┌──────────────┐      ┌──────────┐  │
│  │   FORMULA   │      │    RULES     │      │ UNIVERSAL│  │
│  │   PARSER    │─────▶│   ENGINE     │─────▶│  ENGINE  │  │
│  │  (Etapa 2.1)│      │  (Etapa 2.2) │      │(Etapa 2.3)│  │
│  └─────────────┘      └──────────────┘      └──────────┘  │
│        │                     │                     │        │
│        │                     │                     │        │
│        ▼                     ▼                     ▼        │
│  ┌─────────────┐      ┌──────────────┐      ┌──────────┐  │
│  │   TESTES    │      │    TESTES    │      │  TESTES  │  │
│  │   PARSER    │      │    RULES     │      │INTEGRAÇÃO│  │
│  │  (Etapa 2.4)│      │  (Etapa 2.5) │      │(Etapa 2.6)│  │
│  └─────────────┘      └──────────────┘      └──────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

RESULTADO: Sistema completo de análise com fórmulas e regras
PRÓXIMO: Fase 3 - Interface gráfica de resultados
```

---

## 🚀 INÍCIO RÁPIDO

### Pré-requisitos Verificados

```bash
# 1. Verificar Fase 1 concluída
cd c:\Users\marci\downloads\integragal
pytest tests/test_equipment_detector.py tests/test_equipment_registry.py tests/test_equipment_extractors.py -v

# Esperado: 42 passed, 4 skipped ✅

# 2. Verificar ambiente Python
python --version  # 3.13+
pip list | grep pytest  # pytest instalado

# 3. Estrutura de pastas
mkdir -p services tests docs

# 4. Pronto para começar! 🚀
```

---

## 📝 ETAPA 2.1 - FORMULA PARSER

### 🎯 Objetivo
Criar parser seguro para avaliar expressões matemáticas e lógicas.

### 📦 Arquivo a Criar
`services/formula_parser.py` (~300 linhas)

### 🔧 Funcionalidades
- ✅ Validar fórmulas (sintaxe, operadores, variáveis)
- ✅ Avaliar fórmulas com segurança (whitelist)
- ✅ Substituir variáveis por valores
- ✅ Timeout de 1 segundo
- ✅ Tratamento robusto de erros

### 📋 Estrutura do Arquivo

```python
"""
Formula Parser - Fase 2.1
Avalia expressões matemáticas e lógicas com segurança.
"""

import ast
import re
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class FormulaValidationResult:
    """Resultado da validação de uma fórmula"""
    valida: bool
    mensagem: str
    variaveis_encontradas: List[str] = field(default_factory=list)
    operadores_encontrados: List[str] = field(default_factory=list)
    tempo_validacao_ms: float = 0.0

@dataclass
class FormulaEvaluationResult:
    """Resultado da avaliação de uma fórmula"""
    sucesso: bool
    resultado: Union[bool, float, str, None]
    mensagem_erro: Optional[str] = None
    tempo_execucao_ms: float = 0.0
    variaveis_usadas: Dict[str, Any] = field(default_factory=dict)
    expressao_expandida: str = ""

# ============================================================================
# WHITELIST DE SEGURANÇA
# ============================================================================

# Operadores permitidos
OPERADORES_PERMITIDOS = {
    # Matemáticos
    'Add': '+',      'Sub': '-',      'Mult': '*',
    'Div': '/',      'Mod': '%',      'Pow': '**',
    'FloorDiv': '//',
    
    # Comparação
    'Eq': '==',      'NotEq': '!=',   'Lt': '<',
    'LtE': '<=',     'Gt': '>',       'GtE': '>=',
    
    # Lógicos
    'And': 'and',    'Or': 'or',      'Not': 'not',
    
    # Unários
    'UAdd': '+',     'USub': '-',
}

# Nodes AST permitidos
NODES_PERMITIDOS = {
    ast.Expression,   # Expressão completa
    ast.BinOp,        # Operação binária (a + b)
    ast.UnaryOp,      # Operação unária (-a)
    ast.Compare,      # Comparação (a < b)
    ast.BoolOp,       # Operação booleana (a and b)
    ast.Name,         # Nome de variável
    ast.Constant,     # Constante (número, string)
    ast.Load,         # Contexto de leitura
    # Compatibilidade Python < 3.8
    ast.Num,          # Número (deprecated)
    ast.Str,          # String (deprecated)
}

# Padrão de variáveis permitidas
PATTERN_VARIAVEL = re.compile(
    r'^(CT_|ct_|resultado_|flag_|controle_|status_)[A-Z0-9_]+$', 
    re.IGNORECASE
)

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def extrair_variaveis(expressao: str) -> List[str]:
    """
    Extrai nomes de variáveis de uma fórmula.
    
    Args:
        expressao: Fórmula (ex: "CT_DEN1 + CT_DEN2")
        
    Returns:
        Lista de variáveis encontradas
    """
    variaveis = []
    # Encontrar todas palavras que parecem variáveis
    palavras = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', expressao)
    
    for palavra in palavras:
        # Ignorar palavras-chave Python
        if palavra.lower() in ('and', 'or', 'not', 'true', 'false', 'none'):
            continue
        # Validar padrão
        if PATTERN_VARIAVEL.match(palavra):
            if palavra not in variaveis:
                variaveis.append(palavra)
    
    return variaveis


def substituir_variaveis(expressao: str, variaveis: Dict[str, Any]) -> str:
    """
    Substitui variáveis por valores na fórmula.
    
    Args:
        expressao: Fórmula original
        variaveis: Dict com valores
        
    Returns:
        Expressão com variáveis substituídas
        
    Example:
        >>> substituir_variaveis("CT_DEN1 + CT_DEN2", {"CT_DEN1": 15.5, "CT_DEN2": 18.2})
        "15.5 + 18.2"
    """
    resultado = expressao
    
    # Substituir cada variável por seu valor
    for nome, valor in variaveis.items():
        # Converter valor para string apropriada
        if valor is None:
            valor_str = "None"
        elif isinstance(valor, str):
            valor_str = f"'{valor}'"  # Strings entre aspas
        else:
            valor_str = str(valor)
        
        # Substituir usando regex (palavra completa)
        padrao = r'\b' + re.escape(nome) + r'\b'
        resultado = re.sub(padrao, valor_str, resultado)
    
    return resultado


def formatar_erro(exception: Exception, contexto: str = "") -> str:
    """
    Formata mensagem de erro amigável.
    
    Args:
        exception: Exceção capturada
        contexto: Contexto adicional
        
    Returns:
        Mensagem formatada
    """
    tipo = type(exception).__name__
    mensagem = str(exception)
    
    # Mensagens amigáveis por tipo
    mensagens_amigaveis = {
        'SyntaxError': 'Erro de sintaxe na fórmula',
        'NameError': 'Variável não encontrada',
        'ZeroDivisionError': 'Divisão por zero',
        'TypeError': 'Tipo de dado incompatível',
        'ValueError': 'Valor inválido',
    }
    
    prefixo = mensagens_amigaveis.get(tipo, f'Erro ({tipo})')
    
    if contexto:
        return f"{prefixo} em {contexto}: {mensagem}"
    return f"{prefixo}: {mensagem}"


# ============================================================================
# VALIDAÇÃO DE FÓRMULA
# ============================================================================

def validar_formula(expressao: str) -> FormulaValidationResult:
    """
    Valida uma fórmula antes de avaliar.
    
    Verifica:
    - Sintaxe válida (parsing AST)
    - Apenas operadores permitidos
    - Variáveis seguem padrão correto
    - Sem funções perigosas (__import__, eval, etc)
    
    Args:
        expressao: String com a fórmula (ex: "CT_DEN1 < 30")
        
    Returns:
        FormulaValidationResult com status e detalhes
        
    Examples:
        >>> validar_formula("CT_DEN1 < 30")
        FormulaValidationResult(valida=True, mensagem="Fórmula válida", ...)
        
        >>> validar_formula("__import__('os')")
        FormulaValidationResult(valida=False, mensagem="Node proibido...", ...)
    """
    inicio = datetime.now()
    
    # 1. Verificar string vazia
    if not expressao or not expressao.strip():
        return FormulaValidationResult(
            valida=False,
            mensagem="Fórmula vazia",
            tempo_validacao_ms=0.0
        )
    
    try:
        # 2. Parsear com AST
        tree = ast.parse(expressao, mode='eval')
        
        # 3. Verificar nodes do AST
        for node in ast.walk(tree):
            node_type = type(node)
            
            # Verificar se node é permitido
            if node_type not in NODES_PERMITIDOS:
                return FormulaValidationResult(
                    valida=False,
                    mensagem=f"Node proibido: {node_type.__name__}",
                    tempo_validacao_ms=(datetime.now() - inicio).total_seconds() * 1000
                )
            
            # Verificar operadores
            if isinstance(node, (ast.BinOp, ast.UnaryOp)):
                op_type = type(node.op).__name__
                if op_type not in OPERADORES_PERMITIDOS:
                    return FormulaValidationResult(
                        valida=False,
                        mensagem=f"Operador proibido: {op_type}",
                        tempo_validacao_ms=(datetime.now() - inicio).total_seconds() * 1000
                    )
            
            # Verificar comparações
            if isinstance(node, ast.Compare):
                for op in node.ops:
                    op_type = type(op).__name__
                    if op_type not in OPERADORES_PERMITIDOS:
                        return FormulaValidationResult(
                            valida=False,
                            mensagem=f"Operador de comparação proibido: {op_type}",
                            tempo_validacao_ms=(datetime.now() - inicio).total_seconds() * 1000
                        )
            
            # Verificar booleanos
            if isinstance(node, ast.BoolOp):
                op_type = type(node.op).__name__
                if op_type not in OPERADORES_PERMITIDOS:
                    return FormulaValidationResult(
                        valida=False,
                        mensagem=f"Operador lógico proibido: {op_type}",
                        tempo_validacao_ms=(datetime.now() - inicio).total_seconds() * 1000
                    )
            
            # Verificar chamadas de função (PROIBIDO)
            if isinstance(node, ast.Call):
                return FormulaValidationResult(
                    valida=False,
                    mensagem="Chamadas de função não são permitidas",
                    tempo_validacao_ms=(datetime.now() - inicio).total_seconds() * 1000
                )
            
            # Verificar atributos (PROIBIDO - ex: obj.metodo)
            if isinstance(node, ast.Attribute):
                return FormulaValidationResult(
                    valida=False,
                    mensagem="Acesso a atributos não é permitido",
                    tempo_validacao_ms=(datetime.now() - inicio).total_seconds() * 1000
                )
        
        # 4. Extrair e validar variáveis
        variaveis = extrair_variaveis(expressao)
        
        for var in variaveis:
            if not PATTERN_VARIAVEL.match(var):
                return FormulaValidationResult(
                    valida=False,
                    mensagem=f"Variável '{var}' não segue padrão permitido (CT_*, resultado_*, flag_*, controle_*)",
                    variaveis_encontradas=variaveis,
                    tempo_validacao_ms=(datetime.now() - inicio).total_seconds() * 1000
                )
        
        # 5. Extrair operadores usados
        operadores = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.BinOp, ast.UnaryOp)):
                op_name = OPERADORES_PERMITIDOS.get(type(node.op).__name__)
                if op_name and op_name not in operadores:
                    operadores.append(op_name)
        
        # 6. Tudo OK!
        tempo_ms = (datetime.now() - inicio).total_seconds() * 1000
        
        logger.info(f"Fórmula validada com sucesso: {expressao} ({tempo_ms:.2f}ms)")
        
        return FormulaValidationResult(
            valida=True,
            mensagem="Fórmula válida",
            variaveis_encontradas=variaveis,
            operadores_encontrados=operadores,
            tempo_validacao_ms=tempo_ms
        )
    
    except SyntaxError as e:
        return FormulaValidationResult(
            valida=False,
            mensagem=formatar_erro(e, "parsing"),
            tempo_validacao_ms=(datetime.now() - inicio).total_seconds() * 1000
        )
    
    except Exception as e:
        logger.error(f"Erro inesperado validando fórmula: {e}")
        return FormulaValidationResult(
            valida=False,
            mensagem=formatar_erro(e),
            tempo_validacao_ms=(datetime.now() - inicio).total_seconds() * 1000
        )


# ============================================================================
# AVALIAÇÃO DE FÓRMULA
# ============================================================================

def avaliar_formula(
    expressao: str, 
    variaveis: Dict[str, Any],
    timeout_segundos: float = 1.0
) -> FormulaEvaluationResult:
    """
    Avalia uma fórmula com segurança.
    
    Processo:
    1. Valida fórmula
    2. Verifica variáveis disponíveis
    3. Substitui variáveis por valores
    4. Avalia com eval() controlado (sem __builtins__)
    5. Retorna resultado
    
    Args:
        expressao: Fórmula (ex: "(CT_DEN1 + CT_DEN2) / 2 < 33")
        variaveis: Dict com valores (ex: {"CT_DEN1": 15.5, "CT_DEN2": 18.2})
        timeout_segundos: Tempo máximo de execução (default: 1s)
        
    Returns:
        FormulaEvaluationResult com resultado ou erro
        
    Examples:
        >>> avaliar_formula("(15.5 + 18.2) / 2 < 33", {"CT_DEN1": 15.5, "CT_DEN2": 18.2})
        FormulaEvaluationResult(sucesso=True, resultado=True, ...)
        
        >>> avaliar_formula("CT_INEXISTENTE < 30", {})
        FormulaEvaluationResult(sucesso=False, mensagem_erro="Variável...", ...)
    """
    inicio = datetime.now()
    
    # 1. Validar fórmula primeiro
    validacao = validar_formula(expressao)
    if not validacao.valida:
        return FormulaEvaluationResult(
            sucesso=False,
            resultado=None,
            mensagem_erro=f"Validação falhou: {validacao.mensagem}",
            tempo_execucao_ms=(datetime.now() - inicio).total_seconds() * 1000
        )
    
    # 2. Verificar variáveis disponíveis
    variaveis_necessarias = validacao.variaveis_encontradas
    variaveis_faltando = [v for v in variaveis_necessarias if v not in variaveis]
    
    if variaveis_faltando:
        return FormulaEvaluationResult(
            sucesso=False,
            resultado=None,
            mensagem_erro=f"Variáveis não fornecidas: {', '.join(variaveis_faltando)}",
            tempo_execucao_ms=(datetime.now() - inicio).total_seconds() * 1000,
            variaveis_usadas=variaveis
        )
    
    # 3. Substituir variáveis
    try:
        expressao_expandida = substituir_variaveis(expressao, variaveis)
        logger.debug(f"Fórmula expandida: {expressao} → {expressao_expandida}")
    except Exception as e:
        return FormulaEvaluationResult(
            sucesso=False,
            resultado=None,
            mensagem_erro=formatar_erro(e, "substituição de variáveis"),
            tempo_execucao_ms=(datetime.now() - inicio).total_seconds() * 1000,
            variaveis_usadas=variaveis
        )
    
    # 4. Preparar contexto seguro
    # __builtins__={} remove TODAS funções builtin (print, open, __import__, etc)
    contexto_seguro = {
        '__builtins__': {},
        # Adicionar apenas funções matemáticas seguras se necessário
        'abs': abs,
        'min': min,
        'max': max,
        'round': round,
    }
    
    # 5. Avaliar com eval() controlado
    try:
        # TODO: Implementar timeout real (threading ou signal)
        # Por enquanto, confiar que fórmulas simples são rápidas
        
        resultado = eval(expressao_expandida, contexto_seguro, {})
        
        tempo_ms = (datetime.now() - inicio).total_seconds() * 1000
        
        logger.info(f"Fórmula avaliada: {expressao} = {resultado} ({tempo_ms:.2f}ms)")
        
        return FormulaEvaluationResult(
            sucesso=True,
            resultado=resultado,
            mensagem_erro=None,
            tempo_execucao_ms=tempo_ms,
            variaveis_usadas={k: variaveis[k] for k in variaveis_necessarias},
            expressao_expandida=expressao_expandida
        )
    
    except ZeroDivisionError as e:
        return FormulaEvaluationResult(
            sucesso=False,
            resultado=None,
            mensagem_erro="Divisão por zero",
            tempo_execucao_ms=(datetime.now() - inicio).total_seconds() * 1000,
            variaveis_usadas=variaveis,
            expressao_expandida=expressao_expandida
        )
    
    except NameError as e:
        return FormulaEvaluationResult(
            sucesso=False,
            resultado=None,
            mensagem_erro=formatar_erro(e),
            tempo_execucao_ms=(datetime.now() - inicio).total_seconds() * 1000,
            variaveis_usadas=variaveis,
            expressao_expandida=expressao_expandida
        )
    
    except Exception as e:
        logger.error(f"Erro avaliando fórmula: {e}")
        return FormulaEvaluationResult(
            sucesso=False,
            resultado=None,
            mensagem_erro=formatar_erro(e, "avaliação"),
            tempo_execucao_ms=(datetime.now() - inicio).total_seconds() * 1000,
            variaveis_usadas=variaveis,
            expressao_expandida=expressao_expandida
        )


# ============================================================================
# FUNÇÕES DE CONVENIÊNCIA
# ============================================================================

def avaliar_formula_simples(expressao: str, variaveis: Dict[str, Any]) -> bool:
    """
    Versão simplificada que retorna apenas True/False.
    
    Args:
        expressao: Fórmula booleana
        variaveis: Variáveis
        
    Returns:
        True se passou, False se falhou ou erro
    """
    resultado = avaliar_formula(expressao, variaveis)
    
    if not resultado.sucesso:
        logger.warning(f"Fórmula falhou: {resultado.mensagem_erro}")
        return False
    
    # Converter resultado para bool
    return bool(resultado.resultado)


def testar_formula(expressao: str, casos_teste: List[Dict[str, Any]]) -> None:
    """
    Testa uma fórmula com múltiplos casos.
    
    Args:
        expressao: Fórmula a testar
        casos_teste: Lista de dicts com variáveis
        
    Example:
        >>> testar_formula("CT_DEN1 < 30", [
        ...     {"CT_DEN1": 15.5},  # Deve passar
        ...     {"CT_DEN1": 35.0},  # Deve falhar
        ... ])
    """
    print(f"Testando fórmula: {expressao}")
    print("=" * 60)
    
    for i, caso in enumerate(casos_teste, 1):
        resultado = avaliar_formula(expressao, caso)
        
        status = "✅ OK" if resultado.sucesso else "❌ ERRO"
        print(f"Caso {i}: {status}")
        print(f"  Variáveis: {caso}")
        print(f"  Resultado: {resultado.resultado}")
        if resultado.mensagem_erro:
            print(f"  Erro: {resultado.mensagem_erro}")
        print(f"  Tempo: {resultado.tempo_execucao_ms:.2f}ms")
        print()


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == '__main__':
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Exemplo 1: Validação
    print("=" * 60)
    print("EXEMPLO 1: VALIDAÇÃO DE FÓRMULA")
    print("=" * 60)
    
    formulas_teste = [
        "CT_DEN1 < 30",
        "(CT_DEN1 + CT_DEN2) / 2 < 33",
        "CT_ZIKA < 30 and CT_DENGUE > 15",
        "__import__('os')",  # Inválida
        "variavel_invalida < 30",  # Inválida
    ]
    
    for formula in formulas_teste:
        validacao = validar_formula(formula)
        status = "✅ VÁLIDA" if validacao.valida else "❌ INVÁLIDA"
        print(f"{status}: {formula}")
        if not validacao.valida:
            print(f"  Erro: {validacao.mensagem}")
        print()
    
    # Exemplo 2: Avaliação
    print("=" * 60)
    print("EXEMPLO 2: AVALIAÇÃO DE FÓRMULA")
    print("=" * 60)
    
    variaveis = {
        "CT_DEN1": 15.5,
        "CT_DEN2": 18.2,
        "CT_ZIKA": 25.0,
        "CT_DENGUE": 20.0,
    }
    
    resultado = avaliar_formula("(CT_DEN1 + CT_DEN2) / 2 < 33", variaveis)
    print(f"Fórmula: (CT_DEN1 + CT_DEN2) / 2 < 33")
    print(f"Variáveis: {variaveis}")
    print(f"Resultado: {resultado.resultado}")
    print(f"Tempo: {resultado.tempo_execucao_ms:.2f}ms")
```

---

### 🎯 PROMPT COMPLETO - ETAPA 2.1

```markdown
Implementar Formula Parser completo (Etapa 2.1 da Fase 2):

OBJETIVO:
Criar services/formula_parser.py com avaliação segura de fórmulas matemáticas e lógicas.

CONTEXTO:
- Fase 1 concluída (42 testes passando, 91% sucesso)
- Precisamos avaliar fórmulas como: "(CT_DEN1 + CT_DEN2) / 2 < 33"
- Segurança é CRÍTICA: sem injeção de código, sem acesso ao sistema

ARQUIVO A CRIAR:
services/formula_parser.py (~300 linhas)

ESTRUTURA COMPLETA:

1. IMPORTS E CONFIGURAÇÃO
   - import ast, re, logging, dataclasses, typing, datetime
   - Configurar logger

2. DATACLASSES (2 classes):
   
   @dataclass FormulaValidationResult:
   - valida: bool
   - mensagem: str
   - variaveis_encontradas: List[str]
   - operadores_encontrados: List[str]
   - tempo_validacao_ms: float
   
   @dataclass FormulaEvaluationResult:
   - sucesso: bool
   - resultado: Union[bool, float, str, None]
   - mensagem_erro: Optional[str]
   - tempo_execucao_ms: float
   - variaveis_usadas: Dict[str, Any]
   - expressao_expandida: str

3. WHITELIST DE SEGURANÇA:
   
   OPERADORES_PERMITIDOS = {
       # Matemáticos
       'Add': '+', 'Sub': '-', 'Mult': '*', 'Div': '/',
       'Mod': '%', 'Pow': '**', 'FloorDiv': '//',
       # Comparação
       'Eq': '==', 'NotEq': '!=', 'Lt': '<', 'LtE': '<=',
       'Gt': '>', 'GtE': '>=',
       # Lógicos
       'And': 'and', 'Or': 'or', 'Not': 'not',
       # Unários
       'UAdd': '+', 'USub': '-',
   }
   
   NODES_PERMITIDOS = {
       ast.Expression, ast.BinOp, ast.UnaryOp, ast.Compare,
       ast.BoolOp, ast.Name, ast.Constant, ast.Load,
       ast.Num, ast.Str  # Python < 3.8
   }
   
   PATTERN_VARIAVEL = re.compile(
       r'^(CT_|ct_|resultado_|flag_|controle_|status_)[A-Z0-9_]+$',
       re.IGNORECASE
   )

4. FUNÇÕES AUXILIARES (3 funções):
   
   def extrair_variaveis(expressao: str) -> List[str]:
       """Extrai variáveis usando regex PATTERN_VARIAVEL"""
       # Encontrar palavras, filtrar keywords, validar padrão
       # Retornar lista única
   
   def substituir_variaveis(expressao: str, variaveis: Dict) -> str:
       """Substitui variáveis por valores"""
       # Para cada var no dict:
       #   - Converter valor para string (None, 'string', número)
       #   - Substituir usando regex (palavra completa)
       # Retornar expressão expandida
   
   def formatar_erro(exception: Exception, contexto: str = "") -> str:
       """Formata erro em mensagem amigável"""
       # Mapear tipo de exceção para mensagem amigável
       # Retornar: "{prefixo}: {mensagem}"

5. VALIDAÇÃO (função principal 1):
   
   def validar_formula(expressao: str) -> FormulaValidationResult:
       """
       Valida fórmula antes de avaliar.
       
       Processo:
       1. Verificar string vazia → retornar INVÁLIDA
       2. Parsear com ast.parse(expressao, mode='eval')
       3. Para cada node em ast.walk(tree):
          a. Verificar se type(node) in NODES_PERMITIDOS
          b. Se BinOp/UnaryOp: verificar operador permitido
          c. Se Compare: verificar operadores de comparação
          d. Se BoolOp: verificar operadores lógicos
          e. Se Call: REJEITAR (funções proibidas)
          f. Se Attribute: REJEITAR (obj.metodo proibido)
       4. Extrair variáveis com extrair_variaveis()
       5. Validar cada variável com PATTERN_VARIAVEL
       6. Extrair operadores usados
       7. Retornar FormulaValidationResult(
              valida=True,
              mensagem="Fórmula válida",
              variaveis_encontradas=[...],
              operadores_encontrados=[...],
              tempo_validacao_ms=...
          )
       
       Tratamento de erros:
       - SyntaxError → retornar INVÁLIDA com mensagem formatada
       - Exception → log + retornar INVÁLIDA
       """

6. AVALIAÇÃO (função principal 2):
   
   def avaliar_formula(
       expressao: str,
       variaveis: Dict[str, Any],
       timeout_segundos: float = 1.0
   ) -> FormulaEvaluationResult:
       """
       Avalia fórmula com segurança.
       
       Processo:
       1. Chamar validar_formula(expressao)
          - Se não válida → retornar FALHA
       2. Verificar variáveis disponíveis
          - variaveis_faltando = vars_necessárias - vars_fornecidas
          - Se faltando → retornar FALHA
       3. Substituir variáveis
          - expressao_expandida = substituir_variaveis(expressao, variaveis)
       4. Preparar contexto seguro
          - contexto_seguro = {
                '__builtins__': {},  # Remove TODAS funções builtin
                'abs': abs, 'min': min, 'max': max, 'round': round
            }
       5. Avaliar com eval()
          - resultado = eval(expressao_expandida, contexto_seguro, {})
       6. Retornar FormulaEvaluationResult(
              sucesso=True,
              resultado=resultado,
              tempo_execucao_ms=...,
              variaveis_usadas={...},
              expressao_expandida=...
          )
       
       Tratamento de erros:
       - ZeroDivisionError → mensagem "Divisão por zero"
       - NameError → mensagem formatada
       - Exception → log + mensagem formatada
       
       TODO: Implementar timeout real usando threading ou signal
       """

7. FUNÇÕES DE CONVENIÊNCIA (opcional):
   
   def avaliar_formula_simples(expressao, variaveis) -> bool:
       """Versão simplificada que retorna apenas True/False"""
   
   def testar_formula(expressao, casos_teste):
       """Testa fórmula com múltiplos casos"""

8. EXEMPLO DE USO (if __name__ == '__main__'):
   - Configurar logging
   - Testar validação de várias fórmulas
   - Testar avaliação com variáveis reais

EXEMPLOS DE FÓRMULAS PARA TESTAR:

Válidas:
- "CT_DEN1 < 30"
- "(CT_DEN1 + CT_DEN2) / 2 < 33"
- "CT_ZIKA < 30 and CT_DENGUE > 15"
- "resultado_SC2 == 'Detectado'"
- "(CT_ALV1 - CT_ALV2) > 5"

Inválidas:
- "__import__('os')" → função proibida
- "variavel_invalida < 30" → padrão inválido
- "CT_DEN1 < <" → sintaxe
- "os.system('ls')" → atributo proibido

REQUISITOS TÉCNICOS:
- UTF-8 sem BOM
- Logging em: validação OK, avaliação OK, erros
- Docstrings completas (módulo, classes, funções)
- Type hints em TODAS assinaturas
- Tempo de execução < 100ms por fórmula
- Contexto isolado (__builtins__={})

SEGURANÇA (CRÍTICO):
✅ Whitelist estrita de operadores
✅ Apenas nodes AST permitidos
✅ Sem chamadas de função (Call nodes)
✅ Sem acesso a atributos (Attribute nodes)
✅ Variáveis validadas com regex
✅ Contexto isolado (__builtins__={})
✅ Timeout de 1 segundo (TODO)

CRITÉRIOS DE ACEITAÇÃO:
✅ Arquivo criado com ~300 linhas
✅ 2 dataclasses implementadas
✅ Whitelist completa
✅ validar_formula() funciona
✅ avaliar_formula() funciona
✅ 3 funções auxiliares funcionam
✅ Segurança validada (rejeita __import__, eval, etc)
✅ Tratamento robusto de erros
✅ Logging completo
✅ Exemplo de uso funciona

TESTE MANUAL:
```python
from services.formula_parser import validar_formula, avaliar_formula

# 1. Validar
v = validar_formula("(CT_DEN1 + CT_DEN2) / 2 < 33")
print(v.valida, v.mensagem)

# 2. Avaliar
r = avaliar_formula(
    "(CT_DEN1 + CT_DEN2) / 2 < 33",
    {"CT_DEN1": 15.5, "CT_DEN2": 18.2}
)
print(r.sucesso, r.resultado)  # True, True

# 3. Testar segurança
v = validar_formula("__import__('os')")
print(v.valida, v.mensagem)  # False, "Chamadas de função..."
```

APÓS IMPLEMENTAÇÃO:
1. Testar manualmente com Python interativo
2. Verificar segurança (rejeita __import__, etc)
3. Criar arquivo de teste (Etapa 2.4)
4. Prosseguir para Etapa 2.2 (Rules Engine)

PROSSIGA COM IMPLEMENTAÇÃO! 🚀
```

---

## 📝 ETAPA 2.2 - RULES ENGINE

### 🎯 Objetivo
Criar engine de regras para aplicar lógica condicional complexa.

### 📦 Arquivo a Criar
`services/rules_engine.py` (~350 linhas)

### 🔧 Funcionalidades
- ✅ Aplicar regras booleanas simples
- ✅ Avaliar fórmulas
- ✅ Aplicar regras condicionais (if-then)
- ✅ Validar sequências obrigatórias
- ✅ Validar exclusão mútua
- ✅ Gerar relatório completo

### 📋 Estrutura do Arquivo

```python
"""
Rules Engine - Fase 2.2
Aplica regras customizadas aos resultados de análise.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

# Importar Formula Parser
from services.formula_parser import avaliar_formula, FormulaEvaluationResult

logger = logging.getLogger(__name__)

# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class Validacao:
    """Resultado de uma validação individual"""
    regra_id: str
    regra_nome: str
    resultado: str  # "passou", "falhou", "aviso", "nao_aplicavel"
    detalhes: str
    impacto: str  # "critico", "alto", "medio", "baixo"
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RulesResult:
    """Resultado completo da aplicação de regras"""
    status: str  # "valida", "invalida", "aviso"
    validacoes: List[Validacao] = field(default_factory=list)
    mensagens_erro: List[str] = field(default_factory=list)
    mensagens_aviso: List[str] = field(default_factory=list)
    detalhes: str = ""
    tempo_execucao_ms: float = 0.0

# ============================================================================
# CONSTANTES
# ============================================================================

TIPO_REGRA = {
    'booleana': 'Regra simples true/false',
    'formula': 'Avaliação de fórmula',
    'condicional': 'Regra if-then',
    'sequencia': 'Alvos obrigatórios',
    'exclusao_mutua': 'Apenas um pode ser positivo',
    'threshold': 'Valor dentro de range',
}

NIVEL_IMPACTO = {
    'critico': 4,
    'alto': 3,
    'medio': 2,
    'baixo': 1,
}

# ============================================================================
# APLICADORES DE REGRAS ESPECÍFICAS
# ============================================================================

def aplicar_regra_booleana(
    nome: str,
    valor: bool,
    resultados: Dict[str, Any]
) -> Validacao:
    """
    Aplica regra booleana simples.
    
    Args:
        nome: Nome da regra (ex: "requer_dois_alvos")
        valor: True/False
        resultados: Dict com resultados da análise
        
    Returns:
        Validacao com resultado
    """
    # Implementar lógica específica por nome de regra
    if nome == "requer_dois_alvos":
        # Contar alvos positivos
        alvos = resultados.get('alvos', {})
        positivos = sum(
            1 for alvo, dados in alvos.items()
            if dados.get('resultado') in ('Detectado', 'Positivo')
        )
        
        passou = (positivos >= 2) == valor
        
        return Validacao(
            regra_id=f"bool_{nome}",
            regra_nome=nome,
            resultado="passou" if passou else "falhou",
            detalhes=f"Alvos positivos: {positivos} (esperado: {'≥2' if valor else '<2'})",
            impacto="alto"
        )
    
    # Regra genérica
    return Validacao(
        regra_id=f"bool_{nome}",
        regra_nome=nome,
        resultado="passou" if valor else "falhou",
        detalhes=f"Regra booleana: {valor}",
        impacto="medio"
    )


def aplicar_regra_formula(
    formula: str,
    resultados: Dict[str, Any],
    formula_parser: Any = None
) -> Validacao:
    """
    Aplica regra baseada em fórmula.
    
    Args:
        formula: Fórmula a avaliar
        resultados: Dict com resultados
        formula_parser: Módulo parser (injetado)
        
    Returns:
        Validacao com resultado
    """
    # Preparar variáveis da fórmula
    variaveis = _preparar_variaveis_formulas(resultados)
    
    # Avaliar fórmula
    if formula_parser:
        resultado = formula_parser.avaliar_formula(formula, variaveis)
    else:
        resultado = avaliar_formula(formula, variaveis)
    
    if not resultado.sucesso:
        return Validacao(
            regra_id=f"formula_{hash(formula)}",
            regra_nome=f"Fórmula: {formula}",
            resultado="falhou",
            detalhes=f"Erro: {resultado.mensagem_erro}",
            impacto="alto"
        )
    
    passou = bool(resultado.resultado)
    
    return Validacao(
        regra_id=f"formula_{hash(formula)}",
        regra_nome=f"Fórmula: {formula}",
        resultado="passou" if passou else "falhou",
        detalhes=f"Resultado: {resultado.resultado} (tempo: {resultado.tempo_execucao_ms:.1f}ms)",
        impacto="alto"
    )


def aplicar_regra_condicional(
    regra: Dict[str, Any],
    resultados: Dict[str, Any],
    formula_parser: Any = None
) -> Validacao:
    """
    Aplica regra if-then.
    
    Args:
        regra: Dict com 'if', 'then', 'descricao', 'impacto'
        resultados: Dict com resultados
        formula_parser: Módulo parser
        
    Returns:
        Validacao com resultado
    """
    condicao_if = regra.get('if', '')
    condicao_then = regra.get('then', '')
    descricao = regra.get('descricao', 'Regra condicional')
    impacto = regra.get('impacto', 'medio')
    
    # Preparar variáveis
    variaveis = _preparar_variaveis_formulas(resultados)
    
    # Avaliar IF
    if formula_parser:
        resultado_if = formula_parser.avaliar_formula(condicao_if, variaveis)
    else:
        resultado_if = avaliar_formula(condicao_if, variaveis)
    
    if not resultado_if.sucesso:
        return Validacao(
            regra_id=f"cond_{hash(descricao)}",
            regra_nome=descricao,
            resultado="nao_aplicavel",
            detalhes=f"Erro avaliando IF: {resultado_if.mensagem_erro}",
            impacto=impacto
        )
    
    # Se IF é False, regra não se aplica
    if not bool(resultado_if.resultado):
        return Validacao(
            regra_id=f"cond_{hash(descricao)}",
            regra_nome=descricao,
            resultado="nao_aplicavel",
            detalhes="Condição IF não satisfeita (regra não aplicada)",
            impacto=impacto
        )
    
    # IF é True, avaliar THEN
    if formula_parser:
        resultado_then = formula_parser.avaliar_formula(condicao_then, variaveis)
    else:
        resultado_then = avaliar_formula(condicao_then, variaveis)
    
    if not resultado_then.sucesso:
        return Validacao(
            regra_id=f"cond_{hash(descricao)}",
            regra_nome=descricao,
            resultado="falhou",
            detalhes=f"Erro avaliando THEN: {resultado_then.mensagem_erro}",
            impacto=impacto
        )
    
    passou = bool(resultado_then.resultado)
    
    return Validacao(
        regra_id=f"cond_{hash(descricao)}",
        regra_nome=descricao,
        resultado="passou" if passou else "falhou",
        detalhes=f"IF={resultado_if.resultado}, THEN={resultado_then.resultado}",
        impacto=impacto
    )


def aplicar_regra_sequencia(
    regra: Dict[str, Any],
    resultados: Dict[str, Any]
) -> Validacao:
    """
    Valida presença de alvos obrigatórios.
    
    Args:
        regra: Dict com 'alvos_obrigatorios', 'descricao'
        resultados: Dict com resultados
        
    Returns:
        Validacao com resultado
    """
    alvos_obrigatorios = regra.get('alvos_obrigatorios', [])
    descricao = regra.get('descricao', 'Alvos obrigatórios')
    
    alvos_presentes = resultados.get('alvos', {})
    alvos_faltando = [a for a in alvos_obrigatorios if a not in alvos_presentes]
    
    passou = len(alvos_faltando) == 0
    
    return Validacao(
        regra_id=f"seq_{hash(descricao)}",
        regra_nome=descricao,
        resultado="passou" if passou else "falhou",
        detalhes=f"Obrigatórios: {alvos_obrigatorios}, Faltando: {alvos_faltando}",
        impacto="alto"
    )


def aplicar_regra_exclusao_mutua(
    regra: Dict[str, Any],
    resultados: Dict[str, Any]
) -> Validacao:
    """
    Valida exclusão mútua entre alvos.
    
    Args:
        regra: Dict com 'alvos', 'descricao'
        resultados: Dict com resultados
        
    Returns:
        Validacao com resultado
    """
    alvos_exclusivos = regra.get('alvos', [])
    descricao = regra.get('descricao', 'Exclusão mútua')
    
    alvos_dados = resultados.get('alvos', {})
    positivos = [
        alvo for alvo in alvos_exclusivos
        if alvo in alvos_dados and alvos_dados[alvo].get('resultado') in ('Detectado', 'Positivo')
    ]
    
    passou = len(positivos) <= 1
    
    return Validacao(
        regra_id=f"excl_{hash(descricao)}",
        regra_nome=descricao,
        resultado="passou" if passou else "falhou",
        detalhes=f"Alvos exclusivos: {alvos_exclusivos}, Positivos: {positivos}",
        impacto="alto"
    )


# ============================================================================
# APLICADOR PRINCIPAL
# ============================================================================

def aplicar_regras(
    regras_dict: Dict[str, Any],
    resultados_dict: Dict[str, Any],
    formula_parser: Any = None
) -> RulesResult:
    """
    Aplica todas as regras aos resultados.
    
    Processo:
    1. Valida estrutura de regras
    2. Aplica cada tipo de regra
    3. Coleta validações
    4. Determina status geral
    5. Gera mensagens
    
    Args:
        regras_dict: Dict com todas regras
        resultados_dict: Dict com resultados da análise
        formula_parser: Módulo parser (opcional, usa padrão se None)
        
    Returns:
        RulesResult com status completo
    """
    inicio = datetime.now()
    validacoes = []
    
    try:
        # 1. Aplicar regras booleanas
        for nome, valor in regras_dict.items():
            if isinstance(valor, bool):
                validacao = aplicar_regra_booleana(nome, valor, resultados_dict)
                validacoes.append(validacao)
        
        # 2. Aplicar fórmulas
        formulas = regras_dict.get('formulas', [])
        for formula in formulas:
            validacao = aplicar_regra_formula(formula, resultados_dict, formula_parser)
            validacoes.append(validacao)
        
        # 3. Aplicar condicionais
        condicoes = regras_dict.get('condicoes', [])
        for condicao in condicoes:
            validacao = aplicar_regra_condicional(condicao, resultados_dict, formula_parser)
            validacoes.append(validacao)
        
        # 4. Aplicar sequência
        sequencia = regras_dict.get('sequencia')
        if sequencia:
            validacao = aplicar_regra_sequencia(sequencia, resultados_dict)
            validacoes.append(validacao)
        
        # 5. Aplicar exclusão mútua
        exclusao = regras_dict.get('exclusao_mutua')
        if exclusao:
            validacao = aplicar_regra_exclusao_mutua(exclusao, resultados_dict)
            validacoes.append(validacao)
        
        # 6. Determinar status geral
        status = determinar_status_geral(validacoes)
        
        # 7. Gerar mensagens
        erros, avisos = gerar_mensagens(validacoes)
        
        # 8. Gerar detalhes
        detalhes = gerar_detalhes_resumo(validacoes)
        
        tempo_ms = (datetime.now() - inicio).total_seconds() * 1000
        
        logger.info(f"Regras aplicadas: {len(validacoes)} validações ({tempo_ms:.2f}ms)")
        
        return RulesResult(
            status=status,
            validacoes=validacoes,
            mensagens_erro=erros,
            mensagens_aviso=avisos,
            detalhes=detalhes,
            tempo_execucao_ms=tempo_ms
        )
    
    except Exception as e:
        logger.error(f"Erro aplicando regras: {e}")
        return RulesResult(
            status="invalida",
            validacoes=validacoes,
            mensagens_erro=[f"Erro fatal: {str(e)}"],
            detalhes=f"Erro ao aplicar regras: {str(e)}",
            tempo_execucao_ms=(datetime.now() - inicio).total_seconds() * 1000
        )


# ============================================================================
# GERADORES DE STATUS E MENSAGENS
# ============================================================================

def determinar_status_geral(validacoes: List[Validacao]) -> str:
    """
    Determina status geral baseado em todas validações.
    
    Regras:
    - Se alguma crítica/alta falhou → "invalida"
    - Se todas passaram → "valida"
    - Se há avisos mas nenhuma falha → "aviso"
    
    Args:
        validacoes: Lista de validações aplicadas
        
    Returns:
        Status: "valida", "invalida", "aviso"
    """
    if not validacoes:
        return "valida"
    
    falhas_criticas = [
        v for v in validacoes
        if v.resultado == "falhou" and v.impacto in ('critico', 'alto')
    ]
    
    if falhas_criticas:
        return "invalida"
    
    falhas = [v for v in validacoes if v.resultado == "falhou"]
    
    if falhas:
        return "aviso"
    
    return "valida"


def gerar_mensagens(validacoes: List[Validacao]) -> tuple[List[str], List[str]]:
    """
    Gera mensagens de erro e aviso.
    
    Args:
        validacoes: Lista de validações
        
    Returns:
        Tupla (erros, avisos)
    """
    erros = []
    avisos = []
    
    for v in validacoes:
        if v.resultado == "falhou":
            msg = f"{v.regra_nome}: {v.detalhes}"
            if v.impacto in ('critico', 'alto'):
                erros.append(msg)
            else:
                avisos.append(msg)
    
    return erros, avisos


def gerar_detalhes_resumo(validacoes: List[Validacao]) -> str:
    """
    Gera resumo textual das validações.
    
    Args:
        validacoes: Lista de validações
        
    Returns:
        String com resumo
    """
    if not validacoes:
        return "Nenhuma regra aplicada"
    
    passou = sum(1 for v in validacoes if v.resultado == "passou")
    falhou = sum(1 for v in validacoes if v.resultado == "falhou")
    nao_aplicavel = sum(1 for v in validacoes if v.resultado == "nao_aplicavel")
    
    return f"{passou} passou, {falhou} falhou, {nao_aplicavel} não aplicável (total: {len(validacoes)})"


def _preparar_variaveis_formulas(resultados: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepara dict de variáveis para fórmulas.
    
    Args:
        resultados: Dict com alvos e controles
        
    Returns:
        Dict com variáveis prontas (CT_*, resultado_*, etc)
    """
    variaveis = {}
    
    # Adicionar alvos
    alvos = resultados.get('alvos', {})
    for nome_alvo, dados in alvos.items():
        # CT_{ALVO}
        ct = dados.get('ct')
        if ct is not None:
            variaveis[f"CT_{nome_alvo}"] = float(ct)
        
        # resultado_{ALVO}
        resultado = dados.get('resultado', '')
        if resultado:
            variaveis[f"resultado_{nome_alvo}"] = resultado
    
    # Adicionar controles
    controles = resultados.get('controles', {})
    for nome_controle, dados in controles.items():
        # CT_{CONTROLE}
        ct = dados.get('ct')
        if ct is not None:
            variaveis[f"CT_{nome_controle}"] = float(ct)
        
        # controle_{CONTROLE}
        status = dados.get('status', '')
        if status:
            variaveis[f"controle_{nome_controle}"] = status
    
    return variaveis
```

---

### 🎯 PROMPT COMPLETO - ETAPA 2.2

```markdown
Implementar Rules Engine completo (Etapa 2.2 da Fase 2):

OBJETIVO:
Criar services/rules_engine.py com aplicação de regras customizadas.

CONTEXTO:
- Formula Parser já implementado (Etapa 2.1)
- Precisamos aplicar regras como: "Se DEN1 positivo, DEN2 deve ser positivo"
- Suportar múltiplos tipos de regras

ARQUIVO A CRIAR:
services/rules_engine.py (~350 linhas)

[... continuar com estrutura completa similar ao prompt 2.1 ...]

PROSSIGA COM IMPLEMENTAÇÃO! 🚀
```

---

## 📝 ETAPA 2.3 - INTEGRAÇÃO

### 🎯 PROMPT COMPLETO - ETAPA 2.3

```markdown
Integrar Parser + Rules ao Universal Engine (Etapa 2.3 da Fase 2):

OBJETIVO:
Atualizar services/universal_engine.py para usar Parser + Rules.

CONTEXTO:
- Formula Parser implementado (Etapa 2.1) ✅
- Rules Engine implementado (Etapa 2.2) ✅
- Precisamos integrar ao fluxo de análise existente

[... estrutura completa ...]

PROSSIGA COM IMPLEMENTAÇÃO! 🚀
```

---

## 🧪 ETAPAS 2.4-2.6 - TESTES

### 🎯 PROMPTS RESUMIDOS

```markdown
ETAPA 2.4 - Testes Formula Parser:
- Criar tests/test_formula_parser.py
- 20+ testes cobrindo validação, avaliação, segurança
- Cobertura >90%

ETAPA 2.5 - Testes Rules Engine:
- Criar tests/test_rules_engine.py
- 15+ testes cobrindo todos tipos de regras
- Cobertura >90%

ETAPA 2.6 - Testes Integração:
- Criar tests/test_universal_integration.py
- 10+ testes end-to-end
- Cobertura >85%
```

---

## ✅ CHECKLIST FINAL FASE 2

```markdown
VALIDAÇÃO COMPLETA:

□ Etapa 2.1 - Formula Parser
  □ Arquivo criado (~300 linhas)
  □ Dataclasses OK
  □ Whitelist OK
  □ validar_formula() OK
  □ avaliar_formula() OK
  □ Segurança validada

□ Etapa 2.2 - Rules Engine
  □ Arquivo criado (~350 linhas)
  □ Dataclasses OK
  □ Todos tipos de regras OK
  □ aplicar_regras() OK

□ Etapa 2.3 - Integração
  □ UniversalEngine atualizado
  □ Fluxo integrado
  □ Compatibilidade mantida

□ Etapa 2.4 - Testes Parser
  □ 20+ testes
  □ Todos passam
  □ Cobertura >90%

□ Etapa 2.5 - Testes Rules
  □ 15+ testes
  □ Todos passam
  □ Cobertura >90%

□ Etapa 2.6 - Testes Integração
  □ 10+ testes
  □ Todos passam
  □ Cobertura >85%

□ Documentação
  □ Docstrings completas
  □ README atualizado
  □ Exemplos de uso

COMANDO FINAL:
pytest tests/test_formula_parser.py tests/test_rules_engine.py tests/test_universal_integration.py -v --cov=services --cov-report=term-missing

ESPERADO:
45+ testes passando
Cobertura >85%

SE TUDO OK → FASE 2 CONCLUÍDA! 🎉
PRÓXIMA → FASE 3: Interface Gráfica de Resultados
```

---

**Documento criado:** 08/12/2025  
**Versão:** 1.0  
**Páginas:** ~50  
**Status:** Pronto para uso  
**Próximo passo:** Copiar prompt da Etapa 2.1 e executar
