# -*- coding: utf-8 -*-
"""
Testes para Equipment Registry (Fase 1.6)
Valida carregamento e gerenciamento de configurações de equipamentos
"""
import pytest
from pathlib import Path
from services.equipment_registry import (
    EquipmentConfig,
    EquipmentRegistry,
    get_registry
)


class TestEquipmentConfig:
    """Testes para dataclass EquipmentConfig"""
    
    def test_criar_config_valida(self):
        """Testa criação de configuração válida"""
        config = EquipmentConfig(
            nome='TestEquip',
            modelo='Test Model',
            fabricante='Test Fabricante',
            tipo_placa='96',
            xlsx_estrutura={
                'coluna_well': 0,
                'coluna_sample': 1,
                'coluna_target': 2,
                'coluna_ct': 6,
                'linha_inicio': 9
            },
            extrator_nome='extrair_test',
            formatador_nome='formatar_test'
        )
        
        assert config.nome == 'TestEquip'
        assert config.modelo == 'Test Model'
        assert config.fabricante == 'Test Fabricante'
        assert config.tipo_placa == '96'
        assert config.xlsx_estrutura['coluna_well'] == 0
        assert config.extrator_nome == 'extrair_test'
        assert config.formatador_nome == 'formatar_test'
    
    def test_config_com_estrutura_minima(self):
        """Testa configuração com estrutura mínima"""
        config = EquipmentConfig(
            nome='Minimo',
            modelo='',
            fabricante='',
            tipo_placa='96',
            xlsx_estrutura={
                'coluna_well': 0,
                'coluna_sample': 1,
                'coluna_target': 2,
                'coluna_ct': 5,
                'linha_inicio': 1
            },
            extrator_nome='extrair_generico',
            formatador_nome=''
        )
        
        assert config.nome == 'Minimo'
        assert 'coluna_well' in config.xlsx_estrutura
        assert 'coluna_ct' in config.xlsx_estrutura
        assert 'linha_inicio' in config.xlsx_estrutura


class TestEquipmentRegistry:
    """Testes para classe EquipmentRegistry"""
    
    def test_load_equipamentos_builtin(self):
        """Testa carregamento de equipamentos built-in"""
        registry = EquipmentRegistry()
        registry.load()
        
        # Deve ter equipamentos built-in
        equipamentos = registry.listar_equipamentos()
        assert len(equipamentos) > 0
        
        # Equipamentos esperados
        equipamentos_esperados = ['7500', '7500_Extended', 'CFX96', 'QuantStudio']
        for eq in equipamentos_esperados:
            assert eq in equipamentos, f"Equipamento {eq} não encontrado"
    
    def test_get_equipamento_existente(self):
        """Testa obter equipamento existente"""
        registry = EquipmentRegistry()
        registry.load()
        
        config = registry.get('7500_Extended')
        
        assert config is not None
        assert config.nome == '7500_Extended'
        assert config.modelo is not None
        assert config.fabricante is not None
        assert config.xlsx_estrutura is not None
        assert 'coluna_well' in config.xlsx_estrutura
        assert 'linha_inicio' in config.xlsx_estrutura
    
    def test_get_equipamento_inexistente(self):
        """Testa obter equipamento inexistente"""
        registry = EquipmentRegistry()
        registry.load()
        
        config = registry.get('EquipamentoInexistente123')
        
        assert config is None
    
    def test_get_case_insensitive(self):
        """Testa que get() é case-insensitive"""
        registry = EquipmentRegistry()
        registry.load()
        
        config1 = registry.get('7500_Extended')
        config2 = registry.get('7500_extended')
        config3 = registry.get('7500_EXTENDED')
        
        assert config1 is not None
        assert config2 is not None
        assert config3 is not None
        assert config1.nome == config2.nome == config3.nome
    
    def test_listar_todos(self):
        """Testa listar todas as configurações"""
        registry = EquipmentRegistry()
        registry.load()
        
        configs = registry.listar_todos()
        
        assert isinstance(configs, list)
        assert len(configs) > 0
        assert all(isinstance(c, EquipmentConfig) for c in configs)
    
    def test_listar_equipamentos_retorna_nomes(self):
        """Testa que listar_equipamentos() retorna apenas nomes"""
        registry = EquipmentRegistry()
        registry.load()
        
        nomes = registry.listar_equipamentos()
        
        assert isinstance(nomes, list)
        assert len(nomes) > 0
        assert all(isinstance(n, str) for n in nomes)
        
        # Deve estar ordenado
        assert nomes == sorted(nomes)
    
    def test_registrar_novo_equipamento(self):
        """Testa registrar novo equipamento"""
        registry = EquipmentRegistry()
        registry.load()
        
        novo_config = EquipmentConfig(
            nome='NovoTeste',
            modelo='Modelo Teste',
            fabricante='Fabricante Teste',
            tipo_placa='96',
            xlsx_estrutura={
                'coluna_well': 0,
                'coluna_sample': 1,
                'coluna_target': 2,
                'coluna_ct': 5,
                'linha_inicio': 10
            },
            extrator_nome='extrair_novo',
            formatador_nome='formatar_novo'
        )
        
        registry.registrar_novo(novo_config)
        
        # Verificar se foi registrado
        config_recuperado = registry.get('NovoTeste')
        assert config_recuperado is not None
        assert config_recuperado.nome == 'NovoTeste'
        assert config_recuperado.modelo == 'Modelo Teste'
    
    def test_estrutura_xlsx_valida(self):
        """Testa que estruturas XLSX contêm campos obrigatórios"""
        registry = EquipmentRegistry()
        registry.load()
        
        for config in registry.listar_todos():
            estrutura = config.xlsx_estrutura
            
            # Campos essenciais
            assert 'linha_inicio' in estrutura, f"{config.nome}: falta linha_inicio"
            assert isinstance(estrutura['linha_inicio'], int), f"{config.nome}: linha_inicio deve ser int"
            assert estrutura['linha_inicio'] > 0, f"{config.nome}: linha_inicio deve ser > 0"
            
            # Pelo menos uma coluna de well ou ct
            tem_well = 'coluna_well' in estrutura
            tem_ct = 'coluna_ct' in estrutura
            assert tem_well or tem_ct, f"{config.nome}: deve ter coluna_well ou coluna_ct"


class TestGetRegistrySingleton:
    """Testes para função singleton get_registry()"""
    
    def test_get_registry_retorna_instancia(self):
        """Testa que get_registry() retorna instância válida"""
        registry = get_registry()
        
        assert registry is not None
        assert isinstance(registry, EquipmentRegistry)
    
    def test_get_registry_retorna_mesma_instancia(self):
        """Testa que get_registry() retorna sempre a mesma instância (singleton)"""
        registry1 = get_registry()
        registry2 = get_registry()
        
        assert registry1 is registry2
    
    def test_singleton_ja_carregado(self):
        """Testa que singleton já vem carregado"""
        registry = get_registry()
        equipamentos = registry.listar_equipamentos()
        
        assert len(equipamentos) > 0


class TestValidacoesRegistry:
    """Testes de validações do registry"""
    
    def test_validar_config_sem_nome(self):
        """Testa que configuração sem nome falha validação"""
        # EquipmentConfig valida nome no __post_init__
        with pytest.raises(ValueError, match="Nome do equipamento é obrigatório"):
            config_invalido = EquipmentConfig(
                nome='',  # Nome vazio
                modelo='Test',
                fabricante='Test',
                tipo_placa='96',
                xlsx_estrutura={
                    'coluna_well': 0,
                    'coluna_sample': 1,
                    'coluna_target': 2,
                    'coluna_ct': 5,
                    'linha_inicio': 1
                },
                extrator_nome='test',
                formatador_nome=''
            )
    
    def test_todos_equipamentos_tem_extrator(self):
        """Testa que todos os equipamentos têm extrator definido"""
        registry = EquipmentRegistry()
        registry.load()
        
        for config in registry.listar_todos():
            assert config.extrator_nome, f"{config.nome}: extrator_nome está vazio"
            assert isinstance(config.extrator_nome, str), f"{config.nome}: extrator_nome deve ser string"
            assert len(config.extrator_nome) > 0, f"{config.nome}: extrator_nome está vazio"


class TestIntegracaoRegistry:
    """Testes de integração do registry"""
    
    def test_fluxo_completo_load_get(self):
        """Testa fluxo completo: load → get → validar"""
        registry = EquipmentRegistry()
        
        # 1. Carregar
        registry.load()
        
        # 2. Listar
        equipamentos = registry.listar_equipamentos()
        assert len(equipamentos) > 0
        
        # 3. Obter cada um
        for nome in equipamentos:
            config = registry.get(nome)
            assert config is not None, f"Falhou ao obter config de {nome}"
            assert config.nome == nome
            
            # 4. Validar estrutura
            assert config.xlsx_estrutura is not None
            assert 'linha_inicio' in config.xlsx_estrutura
    
    def test_compatibilidade_com_detector(self):
        """Testa que equipamentos no registry são os mesmos do detector"""
        from services.equipment_detector import obter_padroes_conhecidos
        
        registry = EquipmentRegistry()
        registry.load()
        
        padroes_detector = obter_padroes_conhecidos()
        nomes_detector = {p.nome for p in padroes_detector}  # EquipmentPattern é dataclass
        
        nomes_registry = set(registry.listar_equipamentos())
        
        # Equipamentos do detector devem estar no registry
        for nome in nomes_detector:
            assert nome in nomes_registry, f"Equipamento {nome} do detector não está no registry"
    
    def test_csv_carregamento(self):
        """Testa carregamento do CSV se existir"""
        csv_path = Path('banco/equipamentos.csv')
        
        if csv_path.exists():
            registry = EquipmentRegistry()
            registry.load()
            
            # Deve ter carregado equipamentos do CSV
            equipamentos = registry.listar_equipamentos()
            assert len(equipamentos) >= 4  # Pelo menos os built-in


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
