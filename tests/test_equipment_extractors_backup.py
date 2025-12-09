# -*- coding: utf-8 -*-
"""
Testes para Equipment Extractors (Fase 1.6)
Valida extração e normalização de dados de diferentes equipamentos PCR
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from services.equipment_extractors import (
    extrair_dados_equipamento,
    extrair_7500,
    extrair_7500_extended,
    extrair_cfx96,
    extrair_cfx96_export,
    extrair_quantstudio,
    extrair_generico,
    ExtratorError
)
from services.equipment_registry import get_registry


class TestExtrairDadosEquipamento:
    """Testes para função principal extrair_dados_equipamento()"""
    
    def test_extrair_7500_extended(self):
        """Testa extração de arquivo 7500_Extended"""
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20250718 VR1-VR2 BIOM PLACA 5.xls')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        # Usar configuração do registry
        from services.equipment_registry import get_registry
        registry = get_registry()
        config = registry.get('7500_Extended')
        
        df = extrair_dados_equipamento(str(arquivo), config)
        
        assert df is not None
        assert len(df) > 0
        assert list(df.columns) == ['bem', 'amostra', 'alvo', 'ct']
        assert df['bem'].dtype == object
        assert df['ct'].dtype in [np.float64, np.float32, float]
    
    def test_extrair_quantstudio(self):
        """Testa extração de arquivo QuantStudio"""
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20210809 COVID BIO M PLACA 8_Copy_20210809_182622_Results_20210809 202116.xls')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        config = EquipmentConfig(
            nome='QuantStudio',
            modelo='QuantStudio',
            fabricante='Applied Biosystems',
            tipo_placa='96',
            xlsx_estrutura={
                'coluna_well': 0,
                'coluna_sample': 3,
                'coluna_target': 4,
                'coluna_ct': 12,
                'linha_inicio': 25
            },
            extrator_nome='extrair_quantstudio',
            formatador_nome=''
        )
        
        df = extrair_dados_equipamento(str(arquivo), config)
        
        assert df is not None
        assert len(df) > 0
        assert list(df.columns) == ['bem', 'amostra', 'alvo', 'ct']
    
    def test_extrair_cfx96_export(self):
        """Testa extração de arquivo CFX96_Export"""
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\exemploseegene.xlsx')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        config = EquipmentConfig(
            nome='CFX96_Export',
            modelo='CFX96',
            fabricante='Bio-Rad',
            tipo_placa='96',
            xlsx_estrutura={
                'coluna_well': 2,
                'coluna_sample': 3,
                'coluna_target': 5,
                'coluna_ct': 6,
                'linha_inicio': 3
            },
            extrator_nome='extrair_cfx96_export',
            formatador_nome=''
        )
        
        df = extrair_dados_equipamento(str(arquivo), config)
        
        assert df is not None
        assert len(df) > 0
        assert list(df.columns) == ['bem', 'amostra', 'alvo', 'ct']
    
    def test_extrair_arquivo_inexistente(self):
        """Testa extração com arquivo inexistente"""
        config = EquipmentConfig(
            nome='Test',
            modelo='Test',
            fabricante='Test',
            tipo_placa='96',
            xlsx_estrutura={'linha_inicio': 1},
            extrator_nome='extrair_generico',
            formatador_nome=''
        )
        
        with pytest.raises((FileNotFoundError, ExtratorError, Exception)):
            extrair_dados_equipamento('/caminho/inexistente.xlsx', config)


class TestNormalizacaoDados:
    """Testes de normalização de dados"""
    
    def test_colunas_normalizadas(self):
        """Testa se colunas são normalizadas corretamente"""
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20250718 VR1-VR2 BIOM PLACA 5.xls')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        config = EquipmentConfig(
            nome='7500_Extended',
            modelo='Test',
            fabricante='Test',
            tipo_placa='96',
            xlsx_estrutura={
                'coluna_well': 0,
                'coluna_sample': 1,
                'coluna_target': 2,
                'coluna_ct': 6,
                'linha_inicio': 9
            },
            extrator_nome='extrair_7500_extended',
            formatador_nome=''
        )
        
        df = extrair_dados_equipamento(str(arquivo), config)
        
        # Colunas devem ser exatamente essas
        assert list(df.columns) == ['bem', 'amostra', 'alvo', 'ct']
    
    def test_formato_well_normalizado(self):
        """Testa se formato de well é normalizado (A01, B02, etc.)"""
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20250718 VR1-VR2 BIOM PLACA 5.xls')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        config = EquipmentConfig(
            nome='7500_Extended',
            modelo='Test',
            fabricante='Test',
            tipo_placa='96',
            xlsx_estrutura={
                'coluna_well': 0,
                'coluna_sample': 1,
                'coluna_target': 2,
                'coluna_ct': 6,
                'linha_inicio': 9
            },
            extrator_nome='extrair_7500_extended',
            formatador_nome=''
        )
        
        df = extrair_dados_equipamento(str(arquivo), config)
        
        # Verificar formato de wells
        wells = df['bem'].unique()
        for well in wells[:5]:  # Verificar alguns
            if pd.notna(well):
                # Deve ter formato A01, B02, etc.
                assert len(well) == 3, f"Well {well} não tem 3 caracteres"
                assert well[0].isalpha(), f"Well {well} não começa com letra"
                assert well[1:].isdigit(), f"Well {well} não termina com dígitos"
    
    def test_ct_tipo_float(self):
        """Testa se valores CT são convertidos para float"""
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20250718 VR1-VR2 BIOM PLACA 5.xls')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        config = EquipmentConfig(
            nome='7500_Extended',
            modelo='Test',
            fabricante='Test',
            tipo_placa='96',
            xlsx_estrutura={
                'coluna_well': 0,
                'coluna_sample': 1,
                'coluna_target': 2,
                'coluna_ct': 6,
                'linha_inicio': 9
            },
            extrator_nome='extrair_7500_extended',
            formatador_nome=''
        )
        
        df = extrair_dados_equipamento(str(arquivo), config)
        
        # CT deve ser float (pode ter NaN)
        assert df['ct'].dtype in [np.float64, np.float32, float]
        
        # CTs não-nulos devem ser numéricos válidos
        cts_validos = df[df['ct'].notna()]['ct']
        if len(cts_validos) > 0:
            assert all(isinstance(x, (int, float, np.number)) for x in cts_validos)
    
    def test_remove_linhas_vazias(self):
        """Testa se linhas vazias são removidas"""
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20250718 VR1-VR2 BIOM PLACA 5.xls')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        config = EquipmentConfig(
            nome='7500_Extended',
            modelo='Test',
            fabricante='Test',
            tipo_placa='96',
            xlsx_estrutura={
                'coluna_well': 0,
                'coluna_sample': 1,
                'coluna_target': 2,
                'coluna_ct': 6,
                'linha_inicio': 9
            },
            extrator_nome='extrair_7500_extended',
            formatador_nome=''
        )
        
        df = extrair_dados_equipamento(str(arquivo), config)
        
        # Não deve ter linhas onde bem, amostra E alvo são todos vazios
        linhas_vazias = df[
            df['bem'].isna() & 
            df['amostra'].isna() & 
            df['alvo'].isna()
        ]
        
        assert len(linhas_vazias) == 0, "Há linhas completamente vazias"


class TestValidacoes:
    """Testes de validações dos extractors"""
    
    def test_config_sem_coluna_well(self):
        """Testa que falta de coluna_well é detectada"""
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20250718 VR1-VR2 BIOM PLACA 5.xls')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        config_invalido = EquipmentConfig(
            nome='Test',
            modelo='Test',
            fabricante='Test',
            tipo_placa='96',
            xlsx_estrutura={
                # falta coluna_well
                'coluna_sample': 1,
                'coluna_ct': 6,
                'linha_inicio': 9
            },
            extrator_nome='extrair_7500',
            formatador_nome=''
        )
        
        # Deve levantar erro de validação
        with pytest.raises((ExtratorError, KeyError, Exception)):
            extrair_dados_equipamento(str(arquivo), config_invalido)
    
    def test_linha_inicio_invalida(self):
        """Testa que linha_inicio inválida é tratada"""
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20250718 VR1-VR2 BIOM PLACA 5.xls')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        config_invalido = EquipmentConfig(
            nome='Test',
            modelo='Test',
            fabricante='Test',
            tipo_placa='96',
            xlsx_estrutura={
                'coluna_well': 0,
                'coluna_sample': 1,
                'coluna_target': 2,
                'coluna_ct': 6,
                'linha_inicio': 999999  # Linha muito alta
            },
            extrator_nome='extrair_7500_extended',
            formatador_nome=''
        )
        
        # Pode levantar erro ou retornar DataFrame vazio
        try:
            df = extrair_dados_equipamento(str(arquivo), config_invalido)
            assert len(df) == 0 or df is None
        except (ExtratorError, Exception):
            pass  # Erro é aceitável
    
    def test_target_obrigatorio_cfx96(self):
        """Testa que Target é obrigatório para CFX96"""
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\SC2 20200729-MANAGER.xls')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        config = EquipmentConfig(
            nome='CFX96',
            modelo='CFX96',
            fabricante='Bio-Rad',
            tipo_placa='96',
            xlsx_estrutura={
                'coluna_well': 0,
                'coluna_sample': 4,
                'coluna_target': 2,
                'coluna_ct': 5,
                'linha_inicio': 21
            },
            extrator_nome='extrair_cfx96',
            formatador_nome=''
        )
        
        # Este arquivo específico tem Target vazio
        with pytest.raises(ExtratorError) as exc_info:
            extrair_dados_equipamento(str(arquivo), config)
        
        assert 'Target' in str(exc_info.value) or 'target' in str(exc_info.value).lower()


class TestExtratoresEspecificos:
    """Testes de extratores específicos individuais"""
    
    def test_extrair_7500_direto(self):
        """Testa chamada direta de extrair_7500()"""
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20250718 VR1-VR2 BIOM PLACA 5.xls')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        config = EquipmentConfig(
            nome='7500',
            modelo='Test',
            fabricante='Test',
            tipo_placa='96',
            xlsx_estrutura={
                'coluna_well': 0,
                'coluna_sample': 1,
                'coluna_target': 2,
                'coluna_ct': 6,
                'linha_inicio': 9
            },
            extrator_nome='extrair_7500',
            formatador_nome=''
        )
        
        df = extrair_7500(str(arquivo), config)
        
        assert df is not None
        assert len(df) > 0
        assert list(df.columns) == ['bem', 'amostra', 'alvo', 'ct']
    
    def test_extrair_quantstudio_direto(self):
        """Testa chamada direta de extrair_quantstudio()"""
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20210809 COVID BIO M PLACA 8_Copy_20210809_182622_Results_20210809 202116.xls')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        config = EquipmentConfig(
            nome='QuantStudio',
            modelo='Test',
            fabricante='Test',
            tipo_placa='96',
            xlsx_estrutura={
                'coluna_well': 0,
                'coluna_sample': 3,
                'coluna_target': 4,
                'coluna_ct': 12,
                'linha_inicio': 25
            },
            extrator_nome='extrair_quantstudio',
            formatador_nome=''
        )
        
        df = extrair_quantstudio(str(arquivo), config)
        
        assert df is not None
        assert len(df) > 0


class TestIntegracaoExtractors:
    """Testes de integração dos extractors"""
    
    def test_fluxo_completo_deteccao_extracao(self):
        """Testa fluxo: detectar → carregar config → extrair"""
        from services.equipment_detector import detectar_equipamento
        from services.equipment_registry import EquipmentRegistry
        
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20250718 VR1-VR2 BIOM PLACA 5.xls')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        # 1. Detectar
        resultado = detectar_equipamento(str(arquivo))
        assert resultado is not None
        
        # 2. Carregar config
        registry = EquipmentRegistry()
        registry.load()
        config = registry.get(resultado['equipamento'])
        assert config is not None
        
        # 3. Extrair
        df = extrair_dados_equipamento(str(arquivo), config)
        assert df is not None
        assert len(df) > 0
        assert list(df.columns) == ['bem', 'amostra', 'alvo', 'ct']
    
    def test_multiplos_arquivos_extracao(self):
        """Testa extração de múltiplos arquivos"""
        from services.equipment_detector import detectar_equipamento
        from services.equipment_registry import EquipmentRegistry
        
        arquivos_teste = [
            r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20250718 VR1-VR2 BIOM PLACA 5.xls',
            r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20210809 COVID BIO M PLACA 8_Copy_20210809_182622_Results_20210809 202116.xls',
            r'C:\Users\marci\Downloads\18 JULHO 2025\teste\exemploseegene.xlsx',
        ]
        
        registry = EquipmentRegistry()
        registry.load()
        
        for arquivo_path in arquivos_teste:
            arquivo = Path(arquivo_path)
            if not arquivo.exists():
                continue
            
            # Detectar e extrair
            resultado = detectar_equipamento(str(arquivo))
            config = registry.get(resultado['equipamento'])
            df = extrair_dados_equipamento(str(arquivo), config)
            
            # Validações
            assert df is not None, f"Falhou para {arquivo.name}"
            assert len(df) > 0, f"DataFrame vazio para {arquivo.name}"
            assert list(df.columns) == ['bem', 'amostra', 'alvo', 'ct'], f"Colunas incorretas para {arquivo.name}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
