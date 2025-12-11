# -*- coding: utf-8 -*-
"""Testes unitários para classificação de resultados RT-PCR."""

import pytest
from utils.result_classifier import classificar_resultado
from config.ct_thresholds import VR1E2_THRESHOLDS


class TestValidacaoRP:
    """Testes de validação do controle interno (RP)."""
    
    def test_rp_abaixo_do_minimo(self):
        """RP < 15 deve retornar Invalido."""
        assert classificar_resultado(25.0, 10.0, VR1E2_THRESHOLDS) == "Invalido"
        assert classificar_resultado(25.0, 14.9, VR1E2_THRESHOLDS) == "Invalido"
    
    def test_rp_acima_do_maximo(self):
        """RP > 35 deve retornar Invalido."""
        assert classificar_resultado(25.0, 40.0, VR1E2_THRESHOLDS) == "Invalido"
        assert classificar_resultado(25.0, 35.1, VR1E2_THRESHOLDS) == "Invalido"
    
    def test_rp_ausente(self):
        """RP None deve retornar Invalido."""
        assert classificar_resultado(25.0, None, VR1E2_THRESHOLDS) == "Invalido"
    
    def test_rp_no_limite_minimo(self):
        """RP exatamente 15 deve ser válido."""
        assert classificar_resultado(25.0, 15.0, VR1E2_THRESHOLDS) == "Detectado"
    
    def test_rp_no_limite_maximo(self):
        """RP exatamente 35 deve ser válido."""
        assert classificar_resultado(25.0, 35.0, VR1E2_THRESHOLDS) == "Detectado"
    
    def test_rp_valido_centro_faixa(self):
        """RP no centro da faixa (15-35) deve ser válido."""
        assert classificar_resultado(25.0, 25.0, VR1E2_THRESHOLDS) == "Detectado"
        assert classificar_resultado(25.0, 20.0, VR1E2_THRESHOLDS) == "Detectado"


class TestClassificacaoDetectado:
    """Testes para resultado 'Detectado'."""
    
    def test_ct_baixo_detectado(self):
        """CT <= 38 deve retornar Detectado."""
        assert classificar_resultado(20.0, 25.0, VR1E2_THRESHOLDS) == "Detectado"
        assert classificar_resultado(30.0, 25.0, VR1E2_THRESHOLDS) == "Detectado"
    
    def test_ct_no_limite_detectado(self):
        """CT exatamente 38 deve retornar Detectado."""
        assert classificar_resultado(38.0, 25.0, VR1E2_THRESHOLDS) == "Detectado"
    
    def test_ct_muito_baixo(self):
        """CT muito baixo (alta carga viral) deve ser Detectado."""
        assert classificar_resultado(15.0, 25.0, VR1E2_THRESHOLDS) == "Detectado"


class TestClassificacaoInconclusivo:
    """Testes para resultado 'Inconclusivo'."""
    
    def test_ct_faixa_inconclusiva(self):
        """CT entre 38.01 e 40 deve retornar Inconclusivo."""
        assert classificar_resultado(38.5, 25.0, VR1E2_THRESHOLDS) == "Inconclusivo"
        assert classificar_resultado(39.0, 25.0, VR1E2_THRESHOLDS) == "Inconclusivo"
        assert classificar_resultado(39.5, 25.0, VR1E2_THRESHOLDS) == "Inconclusivo"
    
    def test_ct_limite_inferior_inconclusivo(self):
        """CT exatamente 38.01 deve retornar Inconclusivo."""
        assert classificar_resultado(38.01, 25.0, VR1E2_THRESHOLDS) == "Inconclusivo"
    
    def test_ct_limite_superior_inconclusivo(self):
        """CT exatamente 40 deve retornar Inconclusivo."""
        assert classificar_resultado(40.0, 25.0, VR1E2_THRESHOLDS) == "Inconclusivo"


class TestClassificacaoNaoDetectado:
    """Testes para resultado 'Nao Detectado'."""
    
    def test_ct_acima_limite(self):
        """CT > 40 deve retornar Nao Detectado."""
        assert classificar_resultado(41.0, 25.0, VR1E2_THRESHOLDS) == "Nao Detectado"
        assert classificar_resultado(45.0, 25.0, VR1E2_THRESHOLDS) == "Nao Detectado"
    
    def test_ct_ausente(self):
        """CT None (não amplificou) deve retornar Nao Detectado."""
        assert classificar_resultado(None, 25.0, VR1E2_THRESHOLDS) == "Nao Detectado"


class TestCasosEspeciais:
    """Testes de casos especiais e limites."""
    
    def test_ambos_ausentes(self):
        """CT e RP ausentes deve retornar Invalido (RP inválido)."""
        assert classificar_resultado(None, None, VR1E2_THRESHOLDS) == "Invalido"
    
    def test_ct_zero(self):
        """CT = 0 (valor inválido de equipamento) deve ser tratado."""
        # CT=0 está tecnicamente <= 38, mas é anormal
        # O classificador trata como Detectado (deixa validação para outro lugar)
        assert classificar_resultado(0.0, 25.0, VR1E2_THRESHOLDS) == "Detectado"
    
    def test_ct_negativo(self):
        """CT negativo (erro de equipamento) deve ser tratado."""
        # Classificador trata literalmente a regra <= 38
        assert classificar_resultado(-1.0, 25.0, VR1E2_THRESHOLDS) == "Detectado"


class TestConsistenciaEntreModulos:
    """
    Testes críticos: garantir que TODOS os módulos classificam igual.
    
    Antes da refatoração, tínhamos:
    - vr1e2: CT_DETECTAVEL_MAX = 38
    - universal_engine: CT_DETECTAVEL_MAX = 40 (DIVERGENTE!)
    
    Agora todos devem usar VR1E2_THRESHOLDS.
    """
    
    def test_ct_39_deve_ser_inconclusivo(self):
        """CT=39 era 'Detectado' em alguns módulos, 'Inconclusivo' em outros."""
        # Agora deve ser SEMPRE Inconclusivo
        assert classificar_resultado(39.0, 25.0, VR1E2_THRESHOLDS) == "Inconclusivo"
    
    def test_ct_38_deve_ser_detectado(self):
        """CT=38 deve ser Detectado em TODOS os módulos."""
        assert classificar_resultado(38.0, 25.0, VR1E2_THRESHOLDS) == "Detectado"
    
    def test_ct_40_deve_ser_inconclusivo(self):
        """CT=40 deve ser Inconclusivo em TODOS os módulos."""
        assert classificar_resultado(40.0, 25.0, VR1E2_THRESHOLDS) == "Inconclusivo"
    
    def test_ct_40_01_deve_ser_nao_detectado(self):
        """CT=40.01 deve ser Nao Detectado em TODOS os módulos."""
        assert classificar_resultado(40.01, 25.0, VR1E2_THRESHOLDS) == "Nao Detectado"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
