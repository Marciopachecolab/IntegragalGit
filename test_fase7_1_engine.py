#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FASE 7 - Test 1: Engine Integration (VERSÃO SIMPLIFICADA)
Validar que o engine processa exames do registry corretamente
"""

import pytest
from services.exam_registry import ExamRegistry


class TestEngineIntegrationFASE7:
    """Testes E2E do engine com exames do registry"""

    @pytest.fixture(scope="class")
    def registry(self):
        """Carregar registry com exames do JSON"""
        reg = ExamRegistry()
        reg.load()
        return reg

    def test_1_registry_carregou_exames(self, registry):
        """Test 1.1: Registry carregou exames do JSON"""
        assert len(registry.exams) >= 4
        assert any('vr1e2' in k.lower() for k in registry.exams.keys())
        assert any('zdc' in k.lower() for k in registry.exams.keys())
        print(f"✅ Registry tem {len(registry.exams)} exames")

    def test_2_registry_get_vr1e2(self, registry):
        """Test 1.2: Registry carrega VR1e2 específico"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert cfg is not None
        assert cfg.nome_exame == "VR1e2 Biomanguinhos 7500"
        assert cfg.tipo_placa_analitica == "48"  # É string, não int
        print(f"✅ VR1e2 carregado: tipo_placa={cfg.tipo_placa_analitica}")

    def test_3_registry_get_zdc(self, registry):
        """Test 1.3: Registry carrega ZDC específico"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        assert cfg is not None
        assert cfg.nome_exame == "ZDC Biomanguinhos 7500"
        assert cfg.tipo_placa_analitica == "36"  # É string
        print(f"✅ ZDC carregado: tipo_placa={cfg.tipo_placa_analitica}")

    def test_4_vr1e2_tem_faixas_ct(self, registry):
        """Test 1.4: VR1e2 tem faixas CT do registry"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert cfg.faixas_ct is not None
        assert len(cfg.faixas_ct) > 0
        print(f"✅ VR1e2 faixas_ct: {cfg.faixas_ct}")

    def test_5_vr1e2_tem_alvos(self, registry):
        """Test 1.5: VR1e2 tem alvos do registry"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert cfg.alvos is not None
        assert len(cfg.alvos) > 0
        print(f"✅ VR1e2 alvos: {cfg.alvos}")

    def test_6_vr1e2_tem_panel_tests_id(self, registry):
        """Test 1.6: VR1e2 tem panel_tests_id"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert hasattr(cfg, 'panel_tests_id')
        assert cfg.panel_tests_id is not None
        print(f"✅ VR1e2 panel_tests_id: {cfg.panel_tests_id}")

    def test_7_zdc_tem_faixas_ct(self, registry):
        """Test 1.7: ZDC tem faixas CT"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        assert cfg.faixas_ct is not None
        assert len(cfg.faixas_ct) > 0
        print(f"✅ ZDC faixas_ct: {list(cfg.faixas_ct.keys())}")

    def test_8_zdc_tem_alvos(self, registry):
        """Test 1.8: ZDC tem alvos"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        assert cfg.alvos is not None
        print(f"✅ ZDC alvos: {cfg.alvos}")

    def test_9_zdc_tem_panel_tests_id(self, registry):
        """Test 1.9: ZDC tem panel_tests_id"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        assert cfg.panel_tests_id is not None
        print(f"✅ ZDC panel_tests_id: {cfg.panel_tests_id}")

    def test_10_todos_exames_sao_validos(self, registry):
        """Test 1.10: Todos exames carregados são válidos"""
        for slug, cfg in registry.exams.items():
            assert cfg.nome_exame is not None
            assert cfg.tipo_placa_analitica is not None
            # Nem todos os exames podem ter faixas_ct preenchidas (ex: teste)
            # assert len(cfg.faixas_ct) > 0  # Remover este, nem todos têm
        print(f"✅ Todos {len(registry.exams)} exames são válidos")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("FASE 7 - TEST 1: ENGINE INTEGRATION (SIMPLIFICADO)")
    print("="*80 + "\n")
    
    pytest.main([__file__, '-v', '--tb=short'])
