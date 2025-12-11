# -*- coding: utf-8 -*-
"""Testes para normalização de labels de resultados."""

import pytest
from utils.result_normalizer import normalize_result_label


class TestNormalizacaoDetectado:
    """Testes de normalização para resultado 'Detectado'."""
    
    def test_detectado_maiusculo(self):
        assert normalize_result_label("DETECTADO") == "Detectado"
    
    def test_detectado_normal(self):
        assert normalize_result_label("Detectado") == "Detectado"
    
    def test_det_abreviado(self):
        assert normalize_result_label("Det") == "Detectado"
        assert normalize_result_label("DET") == "Detectado"
    
    def test_positivo_variantes(self):
        assert normalize_result_label("Positivo") == "Detectado"
        assert normalize_result_label("POSITIVO") == "Detectado"
        assert normalize_result_label("POS") == "Detectado"
        assert normalize_result_label("Pos") == "Detectado"


class TestNormalizacaoNaoDetectado:
    """Testes de normalização para resultado 'Nao Detectado'."""
    
    def test_nao_detectado_variantes(self):
        assert normalize_result_label("NAO DETECTADO") == "Nao Detectado"
        assert normalize_result_label("NÃO DETECTADO") == "Nao Detectado"
        assert normalize_result_label("Nao Detectado") == "Nao Detectado"
    
    def test_nd_abreviado(self):
        assert normalize_result_label("ND") == "Nao Detectado"
    
    def test_negativo_variantes(self):
        assert normalize_result_label("Negativo") == "Nao Detectado"
        assert normalize_result_label("NEGATIVO") == "Nao Detectado"
        assert normalize_result_label("NEG") == "Nao Detectado"
        assert normalize_result_label("Neg") == "Nao Detectado"


class TestNormalizacaoInconclusivo:
    """Testes de normalização para resultado 'Inconclusivo'."""
    
    def test_inconclusivo_variantes(self):
        assert normalize_result_label("INCONCLUSIVO") == "Inconclusivo"
        assert normalize_result_label("Inconclusivo") == "Inconclusivo"
    
    def test_inc_abreviado(self):
        assert normalize_result_label("Inc") == "Inconclusivo"
        assert normalize_result_label("INC") == "Inconclusivo"


class TestNormalizacaoInvalido:
    """Testes de normalização para resultado 'Invalido'."""
    
    def test_invalido_variantes(self):
        assert normalize_result_label("INVALIDO") == "Invalido"
        assert normalize_result_label("INVÁLIDO") == "Invalido"
        assert normalize_result_label("Invalido") == "Invalido"


class TestCasosEspeciais:
    """Testes de casos especiais."""
    
    def test_none_retorna_none(self):
        assert normalize_result_label(None) is None
    
    def test_string_desconhecida_retorna_original(self):
        # Se não está no mapeamento, retorna o original
        assert normalize_result_label("DESCONHECIDO") == "DESCONHECIDO"
    
    def test_espacos_sao_removidos(self):
        # A função faz strip()
        assert normalize_result_label("  Det  ") == "Detectado"
        assert normalize_result_label("  ND  ") == "Nao Detectado"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
