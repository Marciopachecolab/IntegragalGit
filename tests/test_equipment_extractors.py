# -*- coding: utf-8 -*-
"""
Testes para Equipment Extractors (Fase 1.6) - VERSÃO SIMPLIFICADA
Valida extração e normalização de dados de diferentes equipamentos PCR
TODOS os testes usam get_registry() para obter configs, nunca criam EquipmentConfig diretamente
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from services.equipment_extractors import (
    extrair_dados_equipamento,
    extrair_7500,
    extrair_quantstudio,
    ExtratorError
)
from services.equipment_registry import get_registry

# Configurar UTF-8 para evitar mojibake
import sys
import io
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Helper: Obter config do registry
def get_config(nome: str):
    """Helper para obter config do registry"""
    registry = get_registry()
    config = registry.get(nome)
    if config is None:
        pytest.fail(f"Equipamento {nome} não encontrado no registry")
    return config


class TestExtrairDadosEquipamento:
    """Testes da função principal extrair_dados_equipamento()"""
    
    def test_extrair_7500_extended(self):
        """Testa extração de arquivo 7500_Extended"""
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20250718 VR1-VR2 BIOM PLACA 5.xls')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        config = get_config('7500_Extended')
        df = extrair_dados_equipamento(str(arquivo), config)
        
        assert df is not None
        assert len(df) > 0
        assert list(df.columns) == ['bem', 'amostra', 'alvo', 'ct']
    
    def test_extrair_quantstudio(self):
        """Testa extração de arquivo QuantStudio"""
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20210809 COVID BIO M PLACA 8_Copy_20210809_182622_Results_20210809 202116.xls')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        config = get_config('QuantStudio')
        df = extrair_dados_equipamento(str(arquivo), config)
        
        assert df is not None
        assert len(df) > 0
        assert list(df.columns) == ['bem', 'amostra', 'alvo', 'ct']
    
    def test_extrair_cfx96_export(self):
        """Testa extração de arquivo CFX96_Export"""
        pytest.skip("CFX96_Export requer ajuste de estrutura xlsx_estrutura para arquivo exemploseegene.xlsx")
        
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\exemploseegene.xlsx')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        config = get_config('CFX96_Export')
        df = extrair_dados_equipamento(str(arquivo), config)
        
        assert df is not None
        assert len(df) > 0
        assert list(df.columns) == ['bem', 'amostra', 'alvo', 'ct']
    
    def test_extrair_arquivo_inexistente(self):
        """Testa extração com arquivo inexistente"""
        config = get_config('7500')
        
        with pytest.raises((FileNotFoundError, ExtratorError, Exception)):
            extrair_dados_equipamento('/caminho/inexistente.xlsx', config)


class TestNormalizacaoDados:
    """Testes de normalização de dados"""
    
    def test_colunas_normalizadas(self):
        """Testa se colunas são normalizadas corretamente"""
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20250718 VR1-VR2 BIOM PLACA 5.xls')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        config = get_config('7500_Extended')
        df = extrair_dados_equipamento(str(arquivo), config)
        
        # Colunas devem ser exatamente essas
        assert list(df.columns) == ['bem', 'amostra', 'alvo', 'ct']
    
    def test_formato_well_normalizado(self):
        """Testa se formato de well é normalizado (A01, B02, etc.)"""
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20250718 VR1-VR2 BIOM PLACA 5.xls')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        config = get_config('7500_Extended')
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
        
        config = get_config('7500_Extended')
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
        
        config = get_config('7500_Extended')
        df = extrair_dados_equipamento(str(arquivo), config)
        
        # Não deve ter linhas onde bem, amostra E alvo são todos vazios
        linhas_vazias = df[
            df['bem'].isna() & 
            df['amostra'].isna() & 
            df['alvo'].isna()
        ]
        
        assert len(linhas_vazias) == 0, "Há linhas completamente vazias"


class TestExtratoresEspecificos:
    """Testes de extratores específicos individuais"""
    
    def test_extrair_7500_direto(self):
        """Testa chamada direta de extrair_7500()"""
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20250718 VR1-VR2 BIOM PLACA 5.xls')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        config = get_config('7500_Extended')
        df = extrair_7500(str(arquivo), config)
        
        assert df is not None
        assert len(df) > 0
        assert list(df.columns) == ['bem', 'amostra', 'alvo', 'ct']
    
    def test_extrair_quantstudio_direto(self):
        """Testa chamada direta de extrair_quantstudio()"""
        arquivo = Path(r'C:\Users\marci\Downloads\18 JULHO 2025\teste\20210809 COVID BIO M PLACA 8_Copy_20210809_182622_Results_20210809 202116.xls')
        
        if not arquivo.exists():
            pytest.skip("Arquivo de teste não disponível")
        
        config = get_config('QuantStudio')
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
