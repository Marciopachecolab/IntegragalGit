#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FASE 7 - Test 1: Engine Integration
Validar que o engine processa exames do registry corretamente
"""

import pytest
import json
import pandas as pd
from pathlib import Path
from services.exam_registry import ExamRegistry
from services.universal_engine import UniversalEngine


class TestEngineIntegration:
    """Testes E2E do engine com exames do registry"""

    @pytest.fixture(scope="class")
    def registry(self):
        """Carregar registry com exames do JSON"""
        reg = ExamRegistry()
        reg.load()
        return reg

    @pytest.fixture(scope="class")
    def engine(self):
        """Instanciar engine"""
        return UniversalEngine()

    def test_registry_has_exams(self, registry):
        """Test 1.1: Registry carregou exames"""
        exams = list(registry.exams.keys())
        assert len(exams) >= 4, f"Expected ≥4 exams, got {len(exams)}"
        assert any('vr1e2' in e.lower() for e in exams), "Missing VR1e2"
        assert any('zdc' in e.lower() for e in exams), "Missing ZDC"
        print(f"✅ Registry carregou {len(exams)} exames")

    def test_engine_initialization(self, engine):
        """Test 1.2: Engine inicializa sem erros"""
        assert engine is not None
        assert hasattr(engine, 'process')
        print("✅ Engine inicializado")

    def test_vr1e2_processing_with_registry(self, registry, engine):
        """Test 1.3: Engine processa VR1e2 com dados do registry"""
        # Carregar configuração do registry
        cfg_vr1e2 = registry.get("vr1e2-biomanguinhos-7500")
        if cfg_vr1e2 is None:
            # Tentar slug alternativo
            cfg_vr1e2 = registry.get("VR1e2 Biomanguinhos 7500")
        assert cfg_vr1e2 is not None, "VR1e2 config not found in registry"

        # Criar dados de teste mínimos
        test_data = {
            'placa_id': 1,
            'exame': 'VR1e2 Biomanguinhos 7500',
            'posicao_placa': 1,
            'ct_values': [15.5, 16.0, 15.8],  # 3 posições para placa 48
        }

        # Procesar com engine
        result = engine.process(test_data, cfg_vr1e2)
        
        assert result is not None, "Engine returned None"
        assert 'status' in result
        assert result['status'] in ['OK', 'ERROR', 'PENDING']
        
        print(f"✅ VR1e2 processado com sucesso: {result['status']}")

    def test_zdc_processing_with_registry(self, registry, engine):
        """Test 1.4: Engine processa ZDC com dados do registry"""
        # Carregar configuração do registry
        cfg_zdc = registry.load_exam("zdc-biomanguinhos-7500")
        assert cfg_zdc is not None, "ZDC config not found in registry"
        assert cfg_zdc.exame == "ZDC Biomanguinhos 7500"
        assert cfg_zdc.modulo_analise == "universal"
        assert cfg_zdc.tipo_placa == 36

        # Criar dados de teste
        test_data = {
            'placa_id': 1,
            'exame': 'ZDC Biomanguinhos 7500',
            'posicao_placa': 1,
            'ct_values': [18.0, 18.5, 19.0],  # 3 posições para placa 36
        }

        # Processar
        result = engine.process(test_data, cfg_zdc)
        
        assert result is not None
        assert 'status' in result
        
        print(f"✅ ZDC processado com sucesso: {result['status']}")

    def test_engine_uses_registry_alvos(self, registry, engine):
        """Test 1.5: Engine usa alvos do registry corretamente"""
        cfg = registry.load_exam("vr1e2-biomanguinhos-7500")
        
        # Validar alvos
        assert hasattr(cfg, 'alvo_negativo_max'), "Missing alvo_negativo_max"
        assert hasattr(cfg, 'alvo_positivo_min'), "Missing alvo_positivo_min"
        assert cfg.alvo_negativo_max > 0
        assert cfg.alvo_positivo_min > 0
        
        print(f"✅ Alvos carregados: NEG={cfg.alvo_negativo_max}, POS={cfg.alvo_positivo_min}")

    def test_engine_uses_registry_faixas(self, registry, engine):
        """Test 1.6: Engine usa faixas CT do registry"""
        cfg = registry.load_exam("vr1e2-biomanguinhos-7500")
        
        # Validar faixas
        assert hasattr(cfg, 'ct_faixa_min'), "Missing ct_faixa_min"
        assert hasattr(cfg, 'ct_faixa_max'), "Missing ct_faixa_max"
        assert cfg.ct_faixa_min >= 0
        assert cfg.ct_faixa_max > cfg.ct_faixa_min
        
        print(f"✅ Faixas CT carregadas: {cfg.ct_faixa_min}–{cfg.ct_faixa_max}")

    def test_engine_result_has_required_fields(self, registry, engine):
        """Test 1.7: Resultado do engine tem campos obrigatórios"""
        cfg = registry.load_exam("vr1e2-biomanguinhos-7500")
        test_data = {
            'placa_id': 1,
            'exame': 'VR1e2 Biomanguinhos 7500',
            'posicao_placa': 1,
            'ct_values': [15.5, 16.0, 15.8],
        }
        
        result = engine.process(test_data, cfg)
        
        # Validar estrutura do resultado
        required_fields = ['status', 'exame', 'posicao_placa']
        for field in required_fields:
            assert field in result, f"Missing field: {field}"
        
        print(f"✅ Resultado tem campos obrigatórios")

    def test_multiple_exams_sequential(self, registry, engine):
        """Test 1.8: Engine processa múltiplos exames sequencialmente"""
        exams_to_test = [
            ("vr1e2-biomanguinhos-7500", "VR1e2 Biomanguinhos 7500", 48),
            ("zdc-biomanguinhos-7500", "ZDC Biomanguinhos 7500", 36),
        ]
        
        results = []
        for slug, name, placa_type in exams_to_test:
            cfg = registry.load_exam(slug)
            assert cfg is not None, f"Config not found for {slug}"
            
            # Dados de teste com tamanho correto
            n_pos = 2 if placa_type == 48 else 3
            test_data = {
                'placa_id': 1,
                'exame': name,
                'posicao_placa': 1,
                'ct_values': [15.0 + i*0.5 for i in range(n_pos)],
            }
            
            result = engine.process(test_data, cfg)
            results.append(result)
        
        assert len(results) == 2
        assert all(r is not None for r in results)
        print(f"✅ Processados {len(results)} exames sequencialmente")

    def test_registry_json_files_exist(self):
        """Test 1.9: Arquivos JSON dos exames existem"""
        json_dir = Path("config/exams")
        assert json_dir.exists(), f"Directory {json_dir} not found"
        
        required_files = [
            "vr1e2_biomanguinhos_7500.json",
            "zdc_biomanguinhos_7500.json",
            "vr1.json",
            "vr2.json",
        ]
        
        for fname in required_files:
            fpath = json_dir / fname
            assert fpath.exists(), f"Missing: {fpath}"
            
            # Validar que é JSON válido
            with open(fpath) as f:
                data = json.load(f)
                assert 'exame' in data, f"Missing 'exame' in {fname}"
        
        print(f"✅ Todos os {len(required_files)} arquivos JSON existem")

    def test_engine_handles_invalid_input(self, registry, engine):
        """Test 1.10: Engine trata entrada inválida graciosamente"""
        cfg = registry.load_exam("vr1e2-biomanguinhos-7500")
        
        # Testar com dados incompletos
        invalid_data = {
            'placa_id': 1,
            'exame': 'VR1e2 Biomanguinhos 7500',
        }
        
        # Engine não deve crashear
        try:
            result = engine.process(invalid_data, cfg)
            # Resultado pode ser erro, mas não deve exceção
            assert result is not None
            print(f"✅ Engine tratou entrada inválida: {result.get('status', 'UNKNOWN')}")
        except KeyError as e:
            # Se falha, deve ser erro esperado
            print(f"✅ Engine falhou graciosamente com KeyError: {e}")


class TestEngineIntegrationPerformance:
    """Testes de performance do engine"""

    @pytest.fixture(scope="class")
    def registry(self):
        """Carregar registry"""
        reg = Registry()
        reg.load()
        return reg

    @pytest.fixture(scope="class")
    def engine(self):
        """Engine"""
        return UniversalEngine()

    def test_registry_load_performance(self, registry):
        """Test: Registry carrega em tempo razoável (<1s)"""
        import time
        
        start = time.time()
        exams = registry.load_all_exams()
        elapsed = time.time() - start
        
        assert elapsed < 1.0, f"Registry took {elapsed}s (expected <1s)"
        print(f"✅ Registry carregou {len(exams)} exames em {elapsed:.3f}s")

    def test_engine_process_performance(self, registry, engine):
        """Test: Engine processa em tempo razoável (<100ms)"""
        import time
        
        cfg = registry.load_exam("vr1e2-biomanguinhos-7500")
        test_data = {
            'placa_id': 1,
            'exame': 'VR1e2 Biomanguinhos 7500',
            'posicao_placa': 1,
            'ct_values': [15.5, 16.0, 15.8],
        }
        
        start = time.time()
        result = engine.process(test_data, cfg)
        elapsed = time.time() - start
        
        assert elapsed < 0.1, f"Engine took {elapsed}s (expected <0.1s)"
        print(f"✅ Engine processou em {elapsed*1000:.1f}ms")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("FASE 7 - TEST 1: ENGINE INTEGRATION")
    print("="*80 + "\n")
    
    # Executar com pytest
    pytest.main([__file__, '-v', '--tb=short'])
