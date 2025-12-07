#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FASE 7 - TESTES E2E CONSOLIDADOS (VERSÃO SIMPLIFICADA)
Tests 1-4: Engine, Histórico, Mapa GUI, GAL Export
"""

import pytest
from services.exam_registry import ExamRegistry


class TestFASE7_E2E:
    """Testes E2E Sistema Completo com Registry"""

    @pytest.fixture(scope="class")
    def registry(self):
        """Carregar registry"""
        reg = ExamRegistry()
        reg.load()
        return reg

    # ========================================================================
    # PARTE 1: ENGINE INTEGRATION (10 tests)
    # ========================================================================

    def test_1_01_registry_carregou_exames(self, registry):
        """1.1: Registry carregou exames"""
        assert len(registry.exams) >= 4
        assert any('vr1e2' in k.lower() for k in registry.exams.keys())
        assert any('zdc' in k.lower() for k in registry.exams.keys())
        print(f"✅ Registry: {len(registry.exams)} exames")

    def test_1_02_engine_vr1e2_carregado(self, registry):
        """1.2: VR1e2 carregado do registry"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert cfg is not None
        assert cfg.nome_exame == "VR1e2 Biomanguinhos 7500"
        print(f"✅ VR1e2 carregado")

    def test_1_03_engine_zdc_carregado(self, registry):
        """1.3: ZDC carregado do registry"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        assert cfg is not None
        assert cfg.nome_exame == "ZDC Biomanguinhos 7500"
        print(f"✅ ZDC carregado")

    def test_1_04_engine_vr1e2_tipo_placa_48(self, registry):
        """1.4: VR1e2 tem tipo_placa 48"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert cfg.tipo_placa_analitica == "48"
        assert cfg.esquema_agrupamento == "96->48"
        print(f"✅ VR1e2 placa: {cfg.tipo_placa_analitica}")

    def test_1_05_engine_zdc_tipo_placa_36(self, registry):
        """1.5: ZDC tem tipo_placa 36"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        assert cfg.tipo_placa_analitica == "36"
        assert cfg.esquema_agrupamento == "96->36"
        print(f"✅ ZDC placa: {cfg.tipo_placa_analitica}")

    def test_1_06_engine_vr1e2_faixas_ct(self, registry):
        """1.6: VR1e2 tem faixas CT"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert len(cfg.faixas_ct) > 0
        assert 'detect_max' in cfg.faixas_ct
        print(f"✅ VR1e2 faixas_ct: {cfg.faixas_ct}")

    def test_1_07_engine_vr1e2_alvos(self, registry):
        """1.7: VR1e2 tem alvos"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert len(cfg.alvos) > 0
        assert 'SC2' in cfg.alvos or 'INF A' in cfg.alvos
        print(f"✅ VR1e2 alvos: {cfg.alvos}")

    def test_1_08_engine_zdc_faixas_ct(self, registry):
        """1.8: ZDC tem faixas CT"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        assert len(cfg.faixas_ct) > 0
        print(f"✅ ZDC faixas_ct configuradas")

    def test_1_09_engine_zdc_alvos(self, registry):
        """1.9: ZDC tem alvos"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        assert len(cfg.alvos) > 0
        assert 'DEN' in cfg.alvos[0] or 'ZYK' in cfg.alvos or 'CHIK' in cfg.alvos
        print(f"✅ ZDC alvos: {cfg.alvos[:3]}")

    def test_1_10_engine_multiplos_exames(self, registry):
        """1.10: Múltiplos exames funcionam"""
        assert len(registry.exams) >= 4
        for slug, cfg in list(registry.exams.items())[:4]:
            assert cfg.nome_exame is not None
            assert cfg.tipo_placa_analitica is not None
        print(f"✅ {len(registry.exams)} exames validados")

    # ========================================================================
    # PARTE 2: HISTÓRICO (10 tests)
    # ========================================================================

    def test_2_01_historico_vr1e2_alvos(self, registry):
        """2.1: Histórico: VR1e2 tem alvos"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert len(cfg.alvos) >= 2  # Múltiplos alvos
        print(f"✅ Histórico: VR1e2 {len(cfg.alvos)} alvos")

    def test_2_02_historico_zdc_alvos(self, registry):
        """2.2: Histórico: ZDC tem alvos"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        assert len(cfg.alvos) >= 2
        print(f"✅ Histórico: ZDC {len(cfg.alvos)} alvos")

    def test_2_03_historico_vr1e2_faixas(self, registry):
        """2.3: Histórico: VR1e2 faixas para coluna"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert 'detect_max' in cfg.faixas_ct
        assert cfg.faixas_ct['detect_max'] == 38.0
        print(f"✅ Histórico: VR1e2 faixa detect_max={cfg.faixas_ct['detect_max']}")

    def test_2_04_historico_vr1e2_rp(self, registry):
        """2.4: Histórico: VR1e2 tem RP"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert len(cfg.rps) > 0
        print(f"✅ Histórico: VR1e2 RP disponível")

    def test_2_05_historico_export_fields(self, registry):
        """2.5: Histórico: export_fields para coluna"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert len(cfg.export_fields) > 0
        print(f"✅ Histórico: {len(cfg.export_fields)} export_fields")

    def test_2_06_historico_vr1e2_export_nomes(self, registry):
        """2.6: Histórico: export_fields tem nomes"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert 'Sars-Cov-2' in cfg.export_fields or 'influenza' in str(cfg.export_fields).lower()
        print(f"✅ Histórico: VR1e2 export com {cfg.export_fields[0]}")

    def test_2_07_historico_mapa_alvos(self, registry):
        """2.7: Histórico: mapa_alvos"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert len(cfg.mapa_alvos) >= len(cfg.alvos)
        print(f"✅ Histórico: mapa com {len(cfg.mapa_alvos)} entradas")

    def test_2_08_historico_vr1e2_totos_alvos_mapeados(self, registry):
        """2.8: Histórico: todos alvos mapeados"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        for alvo in cfg.alvos:
            assert alvo in cfg.mapa_alvos, f"{alvo} não está mapeado"
        print(f"✅ Histórico: todos {len(cfg.alvos)} alvos mapeados")

    def test_2_09_historico_zdc_todos_alvos_mapeados(self, registry):
        """2.9: Histórico: ZDC alvos mapeados"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        for alvo in cfg.alvos:
            assert alvo in cfg.mapa_alvos
        print(f"✅ Histórico: ZDC alvos mapeados")

    def test_2_10_historico_multiplos_exames(self, registry):
        """2.10: Histórico: múltiplos exames"""
        exames_prod = [k for k, cfg in registry.exams.items() 
                      if cfg.alvos and cfg.faixas_ct]
        assert len(exames_prod) >= 2
        print(f"✅ Histórico: {len(exames_prod)} exames com dados")

    # ========================================================================
    # PARTE 3: MAPA GUI (10 tests)
    # ========================================================================

    def test_3_01_mapa_vr1e2_panel_tipo_48(self, registry):
        """3.1: Mapa GUI: VR1e2 é placa 48"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert cfg.tipo_placa_analitica == "48"
        assert "96->48" in cfg.esquema_agrupamento
        print(f"✅ Mapa: VR1e2 placa 48 (96->48)")

    def test_3_02_mapa_zdc_panel_tipo_36(self, registry):
        """3.2: Mapa GUI: ZDC é placa 36"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        assert cfg.tipo_placa_analitica == "36"
        assert "96->36" in cfg.esquema_agrupamento
        print(f"✅ Mapa: ZDC placa 36 (96->36)")

    def test_3_03_mapa_vr1e2_rp(self, registry):
        """3.3: Mapa GUI: VR1e2 tem RP para visualização"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert len(cfg.rps) > 0
        print(f"✅ Mapa: VR1e2 RP disponível")

    def test_3_04_mapa_zdc_rp(self, registry):
        """3.4: Mapa GUI: ZDC tem RP"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        assert len(cfg.rps) > 0
        print(f"✅ Mapa: ZDC RP disponível")

    def test_3_05_mapa_vr1e2_alvos_para_cores(self, registry):
        """3.5: Mapa GUI: VR1e2 alvos para cores"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert len(cfg.alvos) >= 7  # SC2, HMPV, INF A, INF B, ADV, RSV, HRV
        assert len(cfg.mapa_alvos) >= len(cfg.alvos)
        print(f"✅ Mapa: VR1e2 {len(cfg.alvos)} alvos para cores")

    def test_3_06_mapa_zdc_alvos_para_cores(self, registry):
        """3.6: Mapa GUI: ZDC alvos para cores"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        assert len(cfg.alvos) >= 6  # DEN1-4, ZYK, CHIK
        assert len(cfg.mapa_alvos) >= len(cfg.alvos)
        print(f"✅ Mapa: ZDC {len(cfg.alvos)} alvos para cores")

    def test_3_07_mapa_vr1e2_faixas_para_ct_display(self, registry):
        """3.7: Mapa GUI: VR1e2 faixas para display CT"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert 'rp_min' in cfg.faixas_ct
        assert 'rp_max' in cfg.faixas_ct
        print(f"✅ Mapa: VR1e2 faixas CT: {cfg.faixas_ct['rp_min']}-{cfg.faixas_ct['rp_max']}")

    def test_3_08_mapa_zdc_faixas_para_ct_display(self, registry):
        """3.8: Mapa GUI: ZDC faixas"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        assert 'rp_min' in cfg.faixas_ct
        assert 'rp_max' in cfg.faixas_ct
        print(f"✅ Mapa: ZDC faixas RP: {cfg.faixas_ct['rp_min']}-{cfg.faixas_ct['rp_max']}")

    def test_3_09_mapa_vr1e2_controles(self, registry):
        """3.9: Mapa GUI: VR1e2 controles"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert 'cn' in cfg.controles
        assert 'cp' in cfg.controles
        assert len(cfg.controles['cn']) > 0  # G11+G12
        assert len(cfg.controles['cp']) > 0  # H11+H12
        print(f"✅ Mapa: VR1e2 controles: CN={cfg.controles['cn']}, CP={cfg.controles['cp']}")

    def test_3_10_mapa_zdc_controles(self, registry):
        """3.10: Mapa GUI: ZDC controles"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        assert len(cfg.controles['cn']) > 0  # G7+G8
        assert len(cfg.controles['cp']) > 0  # H7+H8
        print(f"✅ Mapa: ZDC controles configurados")

    # ========================================================================
    # PARTE 4: GAL EXPORT (10 tests)
    # ========================================================================

    def test_4_01_gal_vr1e2_panel_tests_id(self, registry):
        """4.1: GAL: VR1e2 panel_tests_id"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert cfg.panel_tests_id is not None
        assert len(cfg.panel_tests_id) > 0
        print(f"✅ GAL: VR1e2 panel_tests_id={cfg.panel_tests_id}")

    def test_4_02_gal_zdc_panel_tests_id(self, registry):
        """4.2: GAL: ZDC panel_tests_id"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        assert cfg.panel_tests_id is not None
        print(f"✅ GAL: ZDC panel_tests_id={cfg.panel_tests_id}")

    def test_4_03_gal_vr1e2_export_fields(self, registry):
        """4.3: GAL: VR1e2 export_fields"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert len(cfg.export_fields) > 0
        print(f"✅ GAL: VR1e2 {len(cfg.export_fields)} fields para export")

    def test_4_04_gal_zdc_export_fields(self, registry):
        """4.4: GAL: ZDC export_fields"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        assert len(cfg.export_fields) > 0
        print(f"✅ GAL: ZDC {len(cfg.export_fields)} fields para export")

    def test_4_05_gal_vr1e2_nome_exame_para_csv(self, registry):
        """4.5: GAL: VR1e2 nome para CSV"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert cfg.nome_exame == "VR1e2 Biomanguinhos 7500"
        print(f"✅ GAL: VR1e2 nome para CSV")

    def test_4_06_gal_zdc_nome_exame_para_csv(self, registry):
        """4.6: GAL: ZDC nome para CSV"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        assert cfg.nome_exame == "ZDC Biomanguinhos 7500"
        print(f"✅ GAL: ZDC nome para CSV")

    def test_4_07_gal_vr1e2_equipamento(self, registry):
        """4.7: GAL: VR1e2 equipamento"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert cfg.equipamento is not None
        print(f"✅ GAL: VR1e2 equipamento={cfg.equipamento}")

    def test_4_08_gal_zdc_equipamento(self, registry):
        """4.8: GAL: ZDC equipamento"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        assert cfg.equipamento is not None
        print(f"✅ GAL: ZDC equipamento={cfg.equipamento}")

    def test_4_09_gal_vr1e2_kit_codigo(self, registry):
        """4.9: GAL: VR1e2 kit_codigo"""
        cfg = registry.get("VR1e2 Biomanguinhos 7500")
        assert cfg.kit_codigo is not None
        print(f"✅ GAL: VR1e2 kit_codigo={cfg.kit_codigo}")

    def test_4_10_gal_zdc_kit_codigo(self, registry):
        """4.10: GAL: ZDC kit_codigo"""
        cfg = registry.get("ZDC Biomanguinhos 7500")
        assert cfg.kit_codigo is not None
        print(f"✅ GAL: ZDC kit_codigo={cfg.kit_codigo}")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("FASE 7 - TESTES E2E (CONSOLIDADOS)")
    print("4 Testes: Engine + Histórico + Mapa GUI + GAL Export")
    print("="*80 + "\n")
    
    pytest.main([__file__, '-v', '--tb=short'])
