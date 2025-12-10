"""
Testes de Performance - Fase 4 Etapa 4.2
Benchmarks de tempo de resposta para validar performance do sistema
"""

import time
import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import random

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

import customtkinter as ctk
from interface import (
    Dashboard,
    VisualizadorExame,
    GraficosQualidade,
    HistoricoAnalises,
    GerenciadorAlertas,
    gerar_alertas_exemplo,
    criar_dados_exame_exemplo
)


class BenchmarkPerformance:
    """Classe para executar benchmarks de performance"""
    
    def __init__(self):
        self.resultados = {}
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
    
    def medir_tempo(self, func, *args, **kwargs):
        """Mede tempo de execução de uma função"""
        inicio = time.perf_counter()
        resultado = func(*args, **kwargs)
        fim = time.perf_counter()
        tempo_ms = (fim - inicio) * 1000
        return tempo_ms, resultado
    
    def benchmark_dashboard_init(self, num_execucoes=3):
        """Benchmark: Tempo de inicialização do Dashboard"""
        print("\n" + "="*70)
        print("BENCHMARK 1: Inicialização do Dashboard")
        print("="*70)
        
        tempos = []
        for i in range(num_execucoes):
            print(f"  Execução {i+1}/{num_execucoes}...", end=" ")
            
            tempo_ms, dashboard = self.medir_tempo(Dashboard)
            tempos.append(tempo_ms)
            
            print(f"{tempo_ms:.2f}ms")
            
            # Destruir para não acumular janelas
            dashboard.destroy()
            
            # Pequeno delay para não sobrecarregar
            time.sleep(0.1)
        
        tempo_medio = sum(tempos) / len(tempos)
        tempo_min = min(tempos)
        tempo_max = max(tempos)
        
        print(f"\n  📊 Resultados:")
        print(f"     Média: {tempo_medio:.2f}ms")
        print(f"     Mínimo: {tempo_min:.2f}ms")
        print(f"     Máximo: {tempo_max:.2f}ms")
        
        # Meta: < 2000ms (2 segundos)
        status = "✅ PASSOU" if tempo_medio < 2000 else "⚠️ ATENÇÃO" if tempo_medio < 3000 else "❌ FALHOU"
        print(f"     Meta: < 2000ms → {status}")
        
        self.resultados['dashboard_init'] = {
            'media': tempo_medio,
            'min': tempo_min,
            'max': tempo_max,
            'meta': 2000,
            'passou': tempo_medio < 2000
        }
        
        return tempo_medio
    
    def benchmark_alertas_geracao(self, num_execucoes=5):
        """Benchmark: Geração de alertas"""
        print("\n" + "="*70)
        print("BENCHMARK 2: Geração de Alertas")
        print("="*70)
        
        tempos = []
        for i in range(num_execucoes):
            print(f"  Execução {i+1}/{num_execucoes}...", end=" ")
            
            gerenciador = GerenciadorAlertas()
            tempo_ms, _ = self.medir_tempo(gerar_alertas_exemplo, gerenciador)
            tempos.append(tempo_ms)
            
            print(f"{tempo_ms:.2f}ms ({len(gerenciador.alertas)} alertas)")
        
        tempo_medio = sum(tempos) / len(tempos)
        tempo_min = min(tempos)
        tempo_max = max(tempos)
        
        print(f"\n  📊 Resultados:")
        print(f"     Média: {tempo_medio:.2f}ms")
        print(f"     Mínimo: {tempo_min:.2f}ms")
        print(f"     Máximo: {tempo_max:.2f}ms")
        
        # Meta: < 100ms
        status = "✅ PASSOU" if tempo_medio < 100 else "⚠️ ATENÇÃO" if tempo_medio < 200 else "❌ FALHOU"
        print(f"     Meta: < 100ms → {status}")
        
        self.resultados['alertas_geracao'] = {
            'media': tempo_medio,
            'min': tempo_min,
            'max': tempo_max,
            'meta': 100,
            'passou': tempo_medio < 100
        }
        
        return tempo_medio
    
    def benchmark_alertas_filtragem(self, num_alertas=1000, num_execucoes=10):
        """Benchmark: Filtragem de alertas"""
        print("\n" + "="*70)
        print(f"BENCHMARK 3: Filtragem de Alertas ({num_alertas} alertas)")
        print("="*70)
        
        # Criar gerenciador com muitos alertas
        print(f"  Gerando {num_alertas} alertas...", end=" ")
        gerenciador = GerenciadorAlertas()
        
        from interface.sistema_alertas import TipoAlerta, CategoriaAlerta, Alerta
        tipos = [TipoAlerta.CRITICO, TipoAlerta.ALTO, TipoAlerta.MEDIO, TipoAlerta.BAIXO, TipoAlerta.INFO]
        categorias = [CategoriaAlerta.CONTROLE, CategoriaAlerta.REGRA, CategoriaAlerta.EQUIPAMENTO, 
                      CategoriaAlerta.SISTEMA, CategoriaAlerta.QUALIDADE]
        
        for i in range(num_alertas):
            tipo = random.choice(tipos)
            categoria = random.choice(categorias)
            alerta = Alerta(tipo, categoria, f"Mensagem de teste {i}")
            gerenciador.adicionar_alerta(alerta)
        
        print(f"✓ {len(gerenciador.alertas)} alertas criados")
        
        # Benchmark de filtragem por tipo
        print(f"\n  Filtragem por tipo:")
        tempos_tipo = []
        for i in range(num_execucoes):
            tempo_ms, _ = self.medir_tempo(gerenciador.get_alertas_por_tipo, TipoAlerta.CRITICO)
            tempos_tipo.append(tempo_ms)
        
        tempo_medio_tipo = sum(tempos_tipo) / len(tempos_tipo)
        print(f"     Média: {tempo_medio_tipo:.2f}ms")
        
        # Benchmark de filtragem por categoria
        print(f"\n  Filtragem por categoria:")
        tempos_categoria = []
        for i in range(num_execucoes):
            tempo_ms, _ = self.medir_tempo(gerenciador.get_alertas_por_categoria, CategoriaAlerta.CONTROLE)
            tempos_categoria.append(tempo_ms)
        
        tempo_medio_categoria = sum(tempos_categoria) / len(tempos_categoria)
        print(f"     Média: {tempo_medio_categoria:.2f}ms")
        
        # Benchmark de não lidos
        print(f"\n  Filtragem não lidos:")
        tempos_nao_lidos = []
        for i in range(num_execucoes):
            tempo_ms, _ = self.medir_tempo(gerenciador.get_alertas_nao_lidos)
            tempos_nao_lidos.append(tempo_ms)
        
        tempo_medio_nao_lidos = sum(tempos_nao_lidos) / len(tempos_nao_lidos)
        print(f"     Média: {tempo_medio_nao_lidos:.2f}ms")
        
        tempo_medio_geral = (tempo_medio_tipo + tempo_medio_categoria + tempo_medio_nao_lidos) / 3
        
        print(f"\n  📊 Resultado Geral:")
        print(f"     Média: {tempo_medio_geral:.2f}ms")
        
        # Meta: < 500ms para 1000 alertas
        status = "✅ PASSOU" if tempo_medio_geral < 500 else "⚠️ ATENÇÃO" if tempo_medio_geral < 1000 else "❌ FALHOU"
        print(f"     Meta: < 500ms → {status}")
        
        self.resultados['alertas_filtragem'] = {
            'media': tempo_medio_geral,
            'num_alertas': num_alertas,
            'meta': 500,
            'passou': tempo_medio_geral < 500
        }
        
        return tempo_medio_geral
    
    def benchmark_dataframe_filtragem(self, num_registros=1000, num_execucoes=10):
        """Benchmark: Filtragem de DataFrames (simulando histórico)"""
        print("\n" + "="*70)
        print(f"BENCHMARK 4: Filtragem de DataFrame ({num_registros} registros)")
        print("="*70)
        
        # Criar DataFrame de teste
        print(f"  Gerando DataFrame com {num_registros} registros...", end=" ")
        dados = {
            'data_analise': [datetime.now() - timedelta(days=random.randint(0, 365)) for _ in range(num_registros)],
            'exame': [f'Exame_{random.randint(1, 50)}' for _ in range(num_registros)],
            'equipamento': [random.choice(['VR1e2', 'Bio7500', 'CFXII', 'Quant5']) for _ in range(num_registros)],
            'resultado': [random.choice(['Detectado', 'Não Detectado', 'Inconclusivo']) for _ in range(num_registros)],
            'ct_value': [random.uniform(15.0, 40.0) if random.random() > 0.3 else None for _ in range(num_registros)],
            'status': [random.choice(['Válido', 'Inválido', 'Revisar']) for _ in range(num_registros)]
        }
        df = pd.DataFrame(dados)
        print(f"✓ DataFrame criado ({df.shape[0]} linhas x {df.shape[1]} colunas)")
        
        # Benchmark: Filtragem por equipamento
        print(f"\n  Filtragem por equipamento:")
        tempos = []
        for i in range(num_execucoes):
            inicio = time.perf_counter()
            df_filtrado = df[df['equipamento'] == 'VR1e2']
            fim = time.perf_counter()
            tempos.append((fim - inicio) * 1000)
        
        tempo_medio = sum(tempos) / len(tempos)
        print(f"     Média: {tempo_medio:.2f}ms ({len(df_filtrado)} resultados)")
        
        # Benchmark: Filtragem por múltiplos critérios
        print(f"\n  Filtragem múltipla (equipamento + resultado + período):")
        tempos_multi = []
        for i in range(num_execucoes):
            inicio = time.perf_counter()
            data_limite = datetime.now() - timedelta(days=30)
            df_filtrado = df[
                (df['equipamento'] == 'VR1e2') &
                (df['resultado'] == 'Detectado') &
                (df['data_analise'] >= data_limite)
            ]
            fim = time.perf_counter()
            tempos_multi.append((fim - inicio) * 1000)
        
        tempo_medio_multi = sum(tempos_multi) / len(tempos_multi)
        print(f"     Média: {tempo_medio_multi:.2f}ms ({len(df_filtrado)} resultados)")
        
        tempo_medio_geral = (tempo_medio + tempo_medio_multi) / 2
        
        print(f"\n  📊 Resultado Geral:")
        print(f"     Média: {tempo_medio_geral:.2f}ms")
        
        # Meta: < 500ms para 1000 registros
        status = "✅ PASSOU" if tempo_medio_geral < 500 else "⚠️ ATENÇÃO" if tempo_medio_geral < 1000 else "❌ FALHOU"
        print(f"     Meta: < 500ms → {status}")
        
        self.resultados['dataframe_filtragem'] = {
            'media': tempo_medio_geral,
            'num_registros': num_registros,
            'meta': 500,
            'passou': tempo_medio_geral < 500
        }
        
        return tempo_medio_geral
    
    def benchmark_exame_criacao(self, num_execucoes=10):
        """Benchmark: Criação de dados de exame"""
        print("\n" + "="*70)
        print("BENCHMARK 5: Criação de Dados de Exame")
        print("="*70)
        
        tempos = []
        for i in range(num_execucoes):
            print(f"  Execução {i+1}/{num_execucoes}...", end=" ")
            
            tempo_ms, dados = self.medir_tempo(criar_dados_exame_exemplo)
            tempos.append(tempo_ms)
            
            print(f"{tempo_ms:.2f}ms")
        
        tempo_medio = sum(tempos) / len(tempos)
        tempo_min = min(tempos)
        tempo_max = max(tempos)
        
        print(f"\n  📊 Resultados:")
        print(f"     Média: {tempo_medio:.2f}ms")
        print(f"     Mínimo: {tempo_min:.2f}ms")
        print(f"     Máximo: {tempo_max:.2f}ms")
        
        # Meta: < 50ms
        status = "✅ PASSOU" if tempo_medio < 50 else "⚠️ ATENÇÃO" if tempo_medio < 100 else "❌ FALHOU"
        print(f"     Meta: < 50ms → {status}")
        
        self.resultados['exame_criacao'] = {
            'media': tempo_medio,
            'min': tempo_min,
            'max': tempo_max,
            'meta': 50,
            'passou': tempo_medio < 50
        }
        
        return tempo_medio
    
    def gerar_relatorio(self):
        """Gera relatório final dos benchmarks"""
        print("\n" + "="*70)
        print("RELATÓRIO FINAL DE PERFORMANCE")
        print("="*70)
        
        print("\n📊 RESUMO DOS BENCHMARKS:\n")
        
        total_testes = len(self.resultados)
        testes_passou = sum(1 for r in self.resultados.values() if r['passou'])
        percentual = (testes_passou / total_testes * 100) if total_testes > 0 else 0
        
        for nome, resultado in self.resultados.items():
            status = "✅" if resultado['passou'] else "❌"
            print(f"  {status} {nome.replace('_', ' ').title()}")
            print(f"     Média: {resultado['media']:.2f}ms | Meta: {resultado['meta']}ms")
            
            if 'num_alertas' in resultado:
                print(f"     Volume: {resultado['num_alertas']} alertas")
            elif 'num_registros' in resultado:
                print(f"     Volume: {resultado['num_registros']} registros")
            
            print()
        
        print(f"📈 TAXA DE SUCESSO: {testes_passou}/{total_testes} ({percentual:.1f}%)")
        
        if percentual == 100:
            print("\n🎉 TODOS OS BENCHMARKS PASSARAM!")
            print("✅ Performance dentro das metas estabelecidas")
        elif percentual >= 80:
            print("\n⚠️ MAIORIA DOS BENCHMARKS PASSOU")
            print("🔧 Otimizações recomendadas para benchmarks que falharam")
        else:
            print("\n❌ PERFORMANCE ABAIXO DO ESPERADO")
            print("🚨 Otimizações críticas necessárias")
        
        print("\n" + "="*70)
        
        return self.resultados


def executar_suite_performance():
    """Executa suite completa de benchmarks de performance"""
    print("\n" + "="*70)
    print("SUITE DE TESTES DE PERFORMANCE - FASE 4 ETAPA 4.2")
    print("="*70)
    print("\n🎯 Objetivo: Validar performance do sistema")
    print("📊 Metas:")
    print("   - Dashboard: < 2000ms")
    print("   - Alertas: < 100ms")
    print("   - Filtragens: < 500ms")
    print("   - Exame: < 50ms")
    print()
    
    benchmark = BenchmarkPerformance()
    
    # Executar benchmarks
    try:
        benchmark.benchmark_dashboard_init(num_execucoes=3)
        benchmark.benchmark_alertas_geracao(num_execucoes=5)
        benchmark.benchmark_alertas_filtragem(num_alertas=1000, num_execucoes=10)
        benchmark.benchmark_dataframe_filtragem(num_registros=1000, num_execucoes=10)
        benchmark.benchmark_exame_criacao(num_execucoes=10)
        
        # Gerar relatório
        resultados = benchmark.gerar_relatorio()
        
        return resultados
        
    except Exception as e:
        print(f"\n❌ Erro durante benchmarks: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    resultados = executar_suite_performance()
    
    # Exit code baseado no resultado
    if resultados:
        passou = sum(1 for r in resultados.values() if r['passou'])
        total = len(resultados)
        sys.exit(0 if passou == total else 1)
    else:
        sys.exit(1)
