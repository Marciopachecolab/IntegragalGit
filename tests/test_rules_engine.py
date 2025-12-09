"""
Testes para Rules Engine - Etapa 2.5
Testa aplicação de regras customizadas aos resultados.
"""

import pytest
from datetime import datetime
from services.rules_engine import (
    Validacao,
    RulesResult,
    aplicar_regra_booleana,
    aplicar_regra_formula,
    aplicar_regra_condicional,
    aplicar_regra_sequencia,
    aplicar_regra_exclusao_mutua,
    aplicar_regras,
    determinar_status_geral,
    gerar_mensagens,
    gerar_detalhes_resumo,
    _preparar_variaveis_formulas,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def resultados_basicos():
    """Resultados de análise para testes"""
    return {
        'alvos': {
            'DEN1': {
                'ct': 18.5,
                'resultado': 'Detectado',
                'status': 'ok'
            },
            'DEN2': {
                'ct': 22.3,
                'resultado': 'Detectado',
                'status': 'ok'
            },
            'ZIKA': {
                'ct': 35.0,
                'resultado': 'Não Detectado',
                'status': 'ok'
            }
        },
        'controles': {
            'IC': {
                'ct': 25.0,
                'status': 'OK'
            }
        }
    }


@pytest.fixture
def resultados_um_alvo():
    """Resultados com apenas um alvo positivo"""
    return {
        'alvos': {
            'DEN1': {
                'ct': 18.5,
                'resultado': 'Detectado',
                'status': 'ok'
            },
            'DEN2': {
                'ct': 35.0,
                'resultado': 'Não Detectado',
                'status': 'ok'
            }
        },
        'controles': {}
    }


@pytest.fixture
def resultados_vazios():
    """Resultados vazios"""
    return {
        'alvos': {},
        'controles': {}
    }


# ============================================================================
# TESTES - REGRAS BOOLEANAS
# ============================================================================

class TestRegraBoolena:
    """Testes para regras booleanas simples"""
    
    def test_requer_dois_alvos_passa(self, resultados_basicos):
        """Teste: requer_dois_alvos=True com 2 alvos positivos deve passar"""
        validacao = aplicar_regra_booleana(
            'requer_dois_alvos',
            True,
            resultados_basicos
        )
        
        assert validacao.resultado == "passou"
        assert validacao.impacto == "alto"
        assert "2" in validacao.detalhes
    
    def test_requer_dois_alvos_falha(self, resultados_um_alvo):
        """Teste: requer_dois_alvos=True com 1 alvo positivo deve falhar"""
        validacao = aplicar_regra_booleana(
            'requer_dois_alvos',
            True,
            resultados_um_alvo
        )
        
        assert validacao.resultado == "falhou"
        assert "1" in validacao.detalhes
    
    def test_requer_dois_alvos_negacao(self, resultados_um_alvo):
        """Teste: requer_dois_alvos=False com 1 alvo positivo deve passar"""
        validacao = aplicar_regra_booleana(
            'requer_dois_alvos',
            False,
            resultados_um_alvo
        )
        
        assert validacao.resultado == "passou"
    
    def test_regra_generica(self, resultados_basicos):
        """Teste: regra booleana genérica"""
        validacao = aplicar_regra_booleana(
            'regra_customizada',
            True,
            resultados_basicos
        )
        
        assert validacao.resultado == "passou"
        assert validacao.impacto == "medio"
        assert "True" in validacao.detalhes


# ============================================================================
# TESTES - REGRAS DE FÓRMULA
# ============================================================================

class TestRegraFormula:
    """Testes para regras baseadas em fórmulas"""
    
    def test_formula_simples_passa(self, resultados_basicos):
        """Teste: fórmula simples que passa"""
        validacao = aplicar_regra_formula(
            "CT_DEN1 < 30",
            resultados_basicos
        )
        
        assert validacao.resultado == "passou"
        assert validacao.impacto == "alto"
        assert "True" in validacao.detalhes
    
    def test_formula_simples_falha(self, resultados_basicos):
        """Teste: fórmula simples que falha"""
        validacao = aplicar_regra_formula(
            "CT_DEN1 > 30",
            resultados_basicos
        )
        
        assert validacao.resultado == "falhou"
        assert "False" in validacao.detalhes
    
    def test_formula_complexa(self, resultados_basicos):
        """Teste: fórmula complexa com múltiplos alvos"""
        validacao = aplicar_regra_formula(
            "(CT_DEN1 + CT_DEN2) / 2 < 25",
            resultados_basicos
        )
        
        assert validacao.resultado == "passou"
        # (18.5 + 22.3) / 2 = 20.4 < 25 → True
    
    def test_formula_logica(self, resultados_basicos):
        """Teste: fórmula com operadores lógicos"""
        validacao = aplicar_regra_formula(
            "CT_DEN1 < 30 and CT_DEN2 < 30",
            resultados_basicos
        )
        
        assert validacao.resultado == "passou"
    
    def test_formula_variavel_faltando(self, resultados_vazios):
        """Teste: fórmula com variável inexistente deve falhar"""
        validacao = aplicar_regra_formula(
            "CT_INEXISTENTE < 30",
            resultados_vazios
        )
        
        assert validacao.resultado == "falhou"
        assert "Erro" in validacao.detalhes


# ============================================================================
# TESTES - REGRAS CONDICIONAIS
# ============================================================================

class TestRegraCondicional:
    """Testes para regras if-then"""
    
    def test_condicional_if_then_passa(self, resultados_basicos):
        """Teste: if True, then True → passa"""
        regra = {
            'if': 'CT_DEN1 < 30',
            'then': 'CT_DEN2 < 30',
            'descricao': 'Se DEN1 positivo, DEN2 deve ser positivo',
            'impacto': 'alto'
        }
        
        validacao = aplicar_regra_condicional(regra, resultados_basicos)
        
        assert validacao.resultado == "passou"
        assert validacao.impacto == "alto"
        assert "IF=True" in validacao.detalhes
        assert "THEN=True" in validacao.detalhes
    
    def test_condicional_if_then_falha(self, resultados_basicos):
        """Teste: if True, then False → falha"""
        regra = {
            'if': 'CT_DEN1 < 30',
            'then': 'CT_ZIKA < 30',  # ZIKA é 35.0
            'descricao': 'Teste falha',
            'impacto': 'medio'
        }
        
        validacao = aplicar_regra_condicional(regra, resultados_basicos)
        
        assert validacao.resultado == "falhou"
        assert "IF=True" in validacao.detalhes
        assert "THEN=False" in validacao.detalhes
    
    def test_condicional_if_false_nao_aplicavel(self, resultados_basicos):
        """Teste: if False → não aplicável"""
        regra = {
            'if': 'CT_DEN1 > 100',  # False
            'then': 'CT_DEN2 < 30',
            'descricao': 'Não se aplica',
            'impacto': 'baixo'
        }
        
        validacao = aplicar_regra_condicional(regra, resultados_basicos)
        
        assert validacao.resultado == "nao_aplicavel"
        assert "não satisfeita" in validacao.detalhes
    
    def test_condicional_erro_if(self, resultados_vazios):
        """Teste: erro avaliando IF"""
        regra = {
            'if': 'CT_INEXISTENTE < 30',
            'then': 'CT_DEN1 < 30',
            'descricao': 'Erro IF',
            'impacto': 'alto'
        }
        
        validacao = aplicar_regra_condicional(regra, resultados_vazios)
        
        assert validacao.resultado == "nao_aplicavel"
        assert "Erro avaliando IF" in validacao.detalhes


# ============================================================================
# TESTES - REGRAS DE SEQUÊNCIA
# ============================================================================

class TestRegraSequencia:
    """Testes para validação de alvos obrigatórios"""
    
    def test_sequencia_todos_presentes(self, resultados_basicos):
        """Teste: todos alvos obrigatórios presentes → passa"""
        regra = {
            'alvos_obrigatorios': ['DEN1', 'DEN2'],
            'descricao': 'Alvos obrigatórios'
        }
        
        validacao = aplicar_regra_sequencia(regra, resultados_basicos)
        
        assert validacao.resultado == "passou"
        assert validacao.impacto == "alto"
        assert "[]" in validacao.detalhes  # Lista vazia de faltando
    
    def test_sequencia_alvos_faltando(self, resultados_um_alvo):
        """Teste: alvos faltando → falha"""
        regra = {
            'alvos_obrigatorios': ['DEN1', 'DEN2', 'ZIKA'],
            'descricao': 'Requer 3 alvos'
        }
        
        validacao = aplicar_regra_sequencia(regra, resultados_um_alvo)
        
        assert validacao.resultado == "falhou"
        assert "ZIKA" in validacao.detalhes
    
    def test_sequencia_vazia(self, resultados_basicos):
        """Teste: lista vazia de obrigatórios → passa"""
        regra = {
            'alvos_obrigatorios': [],
            'descricao': 'Sem obrigatórios'
        }
        
        validacao = aplicar_regra_sequencia(regra, resultados_basicos)
        
        assert validacao.resultado == "passou"


# ============================================================================
# TESTES - REGRAS DE EXCLUSÃO MÚTUA
# ============================================================================

class TestRegraExclusaoMutua:
    """Testes para validação de exclusão mútua"""
    
    def test_exclusao_um_positivo_passa(self, resultados_um_alvo):
        """Teste: apenas um positivo → passa"""
        regra = {
            'alvos': ['DEN1', 'DEN2'],
            'descricao': 'DEN1 e DEN2 são mutuamente exclusivos'
        }
        
        validacao = aplicar_regra_exclusao_mutua(regra, resultados_um_alvo)
        
        assert validacao.resultado == "passou"
        assert validacao.impacto == "alto"
    
    def test_exclusao_dois_positivos_falha(self, resultados_basicos):
        """Teste: dois positivos → falha"""
        regra = {
            'alvos': ['DEN1', 'DEN2'],
            'descricao': 'Exclusão mútua'
        }
        
        validacao = aplicar_regra_exclusao_mutua(regra, resultados_basicos)
        
        assert validacao.resultado == "falhou"
        assert "DEN1" in validacao.detalhes
        assert "DEN2" in validacao.detalhes
    
    def test_exclusao_nenhum_positivo_passa(self, resultados_vazios):
        """Teste: nenhum positivo → passa"""
        regra = {
            'alvos': ['DEN1', 'DEN2', 'ZIKA'],
            'descricao': 'Exclusão mútua'
        }
        
        validacao = aplicar_regra_exclusao_mutua(regra, resultados_vazios)
        
        assert validacao.resultado == "passou"


# ============================================================================
# TESTES - APLICAÇÃO COMPLETA
# ============================================================================

class TestAplicarRegras:
    """Testes para aplicação completa de múltiplas regras"""
    
    def test_aplicar_varias_regras(self, resultados_basicos):
        """Teste: aplicar múltiplas regras de diferentes tipos"""
        regras = {
            'requer_dois_alvos': True,
            'formulas': [
                'CT_DEN1 < 30',
                'CT_DEN2 < 30'
            ],
            'condicoes': [
                {
                    'if': 'CT_DEN1 < 30',
                    'then': 'CT_DEN2 < 30',
                    'descricao': 'DEN1 e DEN2 consistentes',
                    'impacto': 'alto'
                }
            ],
            'sequencia': {
                'alvos_obrigatorios': ['DEN1', 'DEN2'],
                'descricao': 'Alvos obrigatórios'
            }
        }
        
        resultado = aplicar_regras(regras, resultados_basicos)
        
        assert resultado.status in ("valida", "aviso")
        assert len(resultado.validacoes) >= 5
        assert resultado.tempo_execucao_ms > 0
    
    def test_aplicar_regras_status_valida(self, resultados_basicos):
        """Teste: todas regras passam → status valida"""
        regras = {
            'formulas': ['CT_DEN1 < 30']
        }
        
        resultado = aplicar_regras(regras, resultados_basicos)
        
        assert resultado.status == "valida"
        assert len(resultado.mensagens_erro) == 0
    
    def test_aplicar_regras_status_invalida(self, resultados_basicos):
        """Teste: regra crítica falha → status invalida"""
        regras = {
            'formulas': ['CT_DEN1 > 100']  # Falha
        }
        
        resultado = aplicar_regras(regras, resultados_basicos)
        
        assert resultado.status == "invalida"
        assert len(resultado.mensagens_erro) > 0
    
    def test_aplicar_regras_vazias(self, resultados_basicos):
        """Teste: sem regras → status valida"""
        regras = {}
        
        resultado = aplicar_regras(regras, resultados_basicos)
        
        assert resultado.status == "valida"
        assert len(resultado.validacoes) == 0


# ============================================================================
# TESTES - FUNÇÕES AUXILIARES
# ============================================================================

class TestFuncoesAuxiliares:
    """Testes para funções auxiliares"""
    
    def test_determinar_status_geral_valida(self):
        """Teste: todas validações passam → valida"""
        validacoes = [
            Validacao('1', 'Teste 1', 'passou', 'OK', 'alto'),
            Validacao('2', 'Teste 2', 'passou', 'OK', 'medio'),
        ]
        
        status = determinar_status_geral(validacoes)
        assert status == "valida"
    
    def test_determinar_status_geral_invalida(self):
        """Teste: falha crítica → invalida"""
        validacoes = [
            Validacao('1', 'Teste 1', 'passou', 'OK', 'alto'),
            Validacao('2', 'Teste 2', 'falhou', 'Erro', 'critico'),
        ]
        
        status = determinar_status_geral(validacoes)
        assert status == "invalida"
    
    def test_determinar_status_geral_aviso(self):
        """Teste: falha baixa → aviso"""
        validacoes = [
            Validacao('1', 'Teste 1', 'passou', 'OK', 'alto'),
            Validacao('2', 'Teste 2', 'falhou', 'Aviso', 'baixo'),
        ]
        
        status = determinar_status_geral(validacoes)
        assert status == "aviso"
    
    def test_gerar_mensagens(self):
        """Teste: geração de mensagens de erro e aviso"""
        validacoes = [
            Validacao('1', 'Teste 1', 'passou', 'OK', 'alto'),
            Validacao('2', 'Teste 2', 'falhou', 'Erro crítico', 'critico'),
            Validacao('3', 'Teste 3', 'falhou', 'Aviso menor', 'baixo'),
        ]
        
        erros, avisos = gerar_mensagens(validacoes)
        
        assert len(erros) == 1
        assert "Teste 2" in erros[0]
        assert len(avisos) == 1
        assert "Teste 3" in avisos[0]
    
    def test_gerar_detalhes_resumo(self):
        """Teste: geração de resumo textual"""
        validacoes = [
            Validacao('1', 'Teste 1', 'passou', 'OK', 'alto'),
            Validacao('2', 'Teste 2', 'falhou', 'Erro', 'medio'),
            Validacao('3', 'Teste 3', 'nao_aplicavel', 'N/A', 'baixo'),
        ]
        
        detalhes = gerar_detalhes_resumo(validacoes)
        
        assert "1 passou" in detalhes
        assert "1 falhou" in detalhes
        assert "1 não aplicável" in detalhes
        assert "total: 3" in detalhes
    
    def test_preparar_variaveis_formulas(self, resultados_basicos):
        """Teste: preparação de variáveis para fórmulas"""
        variaveis = _preparar_variaveis_formulas(resultados_basicos)
        
        # Verificar alvos
        assert 'CT_DEN1' in variaveis
        assert variaveis['CT_DEN1'] == 18.5
        assert 'CT_DEN2' in variaveis
        assert variaveis['CT_DEN2'] == 22.3
        assert 'resultado_DEN1' in variaveis
        assert variaveis['resultado_DEN1'] == 'Detectado'
        
        # Verificar controles
        assert 'CT_IC' in variaveis
        assert variaveis['CT_IC'] == 25.0
        assert 'controle_IC' in variaveis
        assert variaveis['controle_IC'] == 'OK'


# ============================================================================
# TESTES - INTEGRAÇÃO E PERFORMANCE
# ============================================================================

class TestIntegracao:
    """Testes de integração e performance"""
    
    def test_workflow_completo(self, resultados_basicos):
        """Teste: workflow completo de aplicação de regras"""
        # 1. Definir regras
        regras = {
            'requer_dois_alvos': True,
            'formulas': ['CT_DEN1 < 30', 'CT_DEN2 < 30'],
            'condicoes': [{
                'if': 'CT_DEN1 < 30',
                'then': 'CT_DEN2 < 30',
                'descricao': 'Consistência',
                'impacto': 'alto'
            }]
        }
        
        # 2. Aplicar regras
        resultado = aplicar_regras(regras, resultados_basicos)
        
        # 3. Verificar resultado completo
        assert isinstance(resultado, RulesResult)
        assert resultado.status in ("valida", "invalida", "aviso")
        assert len(resultado.validacoes) > 0
        assert isinstance(resultado.mensagens_erro, list)
        assert isinstance(resultado.mensagens_aviso, list)
        assert resultado.detalhes != ""
        assert resultado.tempo_execucao_ms > 0
    
    def test_performance_multiplas_regras(self, resultados_basicos):
        """Teste: aplicar 10+ regras em < 100ms"""
        regras = {
            'formulas': [
                f'CT_DEN1 < {30 + i}' for i in range(10)
            ]
        }
        
        resultado = aplicar_regras(regras, resultados_basicos)
        
        assert resultado.tempo_execucao_ms < 100
        assert len(resultado.validacoes) == 10
    
    def test_diferentes_tipos_resultados(self):
        """Teste: trabalhar com diferentes tipos de resultados"""
        # Resultados com strings, booleanos, números
        resultados = {
            'alvos': {
                'TARGET1': {
                    'ct': 15.0,
                    'resultado': 'Positivo',
                    'status': 'ok'
                }
            },
            'controles': {}
        }
        
        regras = {
            'formulas': ['CT_TARGET1 < 20']
        }
        
        resultado = aplicar_regras(regras, resultados)
        
        assert resultado.status == "valida"


# ============================================================================
# TESTES - CASOS EXTREMOS
# ============================================================================

class TestCasosExtremos:
    """Testes para casos extremos e edge cases"""
    
    def test_resultados_vazios(self, resultados_vazios):
        """Teste: aplicar regras em resultados vazios"""
        regras = {
            'formulas': ['CT_DEN1 < 30']
        }
        
        resultado = aplicar_regras(regras, resultados_vazios)
        
        # Deve falhar mas não crashar
        assert resultado.status == "invalida"
    
    def test_regras_malformadas(self, resultados_basicos):
        """Teste: lidar com regras malformadas"""
        regras = {
            'condicoes': [
                {
                    # Faltando 'if' e 'then'
                    'descricao': 'Regra incompleta'
                }
            ]
        }
        
        # Não deve crashar
        resultado = aplicar_regras(regras, resultados_basicos)
        assert isinstance(resultado, RulesResult)
    
    def test_muitas_validacoes(self, resultados_basicos):
        """Teste: processar muitas validações (stress test)"""
        regras = {
            'formulas': [f'CT_DEN1 < {i}' for i in range(50, 100)]
        }
        
        resultado = aplicar_regras(regras, resultados_basicos)
        
        assert len(resultado.validacoes) == 50
        assert resultado.tempo_execucao_ms < 500  # < 500ms para 50 regras
