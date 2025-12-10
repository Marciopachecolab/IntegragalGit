"""
Testes de Memória e Stress - Fase 4 Etapa 4.2
Profiling de memória e testes com grandes volumes
"""

import sys
import os
from pathlib import Path
import gc
import random
from datetime import datetime, timedelta

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

import customtkinter as ctk
from interface import GerenciadorAlertas, gerar_alertas_exemplo
from interface.sistema_alertas import TipoAlerta, CategoriaAlerta, Alerta


def get_memory_usage():
    """Retorna uso de memória em MB (aproximado)"""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # Converter para MB
    except ImportError:
        # Fallback se psutil não estiver disponível
        return None


class TestMemoriaStress:
    """Testes de memória e stress"""
    
    def __init__(self):
        self.resultados = {}
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
    
    def test_memoria_baseline(self):
        """Teste 1: Medição de memória baseline"""
        print("\n" + "="*70)
        print("TESTE 1: Memória Baseline")
        print("="*70)
        
        # Forçar garbage collection
        gc.collect()
        
        mem_inicial = get_memory_usage()
        
        if mem_inicial is None:
            print("  ⚠️ psutil não disponível - pulando teste de memória")
            print("  💡 Instale com: pip install psutil")
            return None
        
        print(f"  Memória inicial: {mem_inicial:.2f} MB")
        
        # Criar instâncias básicas
        gerenciador = GerenciadorAlertas()
        gerar_alertas_exemplo(gerenciador)
        
        mem_apos_alertas = get_memory_usage()
        print(f"  Memória após 8 alertas: {mem_apos_alertas:.2f} MB")
        print(f"  Delta: +{(mem_apos_alertas - mem_inicial):.2f} MB")
        
        self.resultados['memoria_baseline'] = {
            'inicial': mem_inicial,
            'apos_alertas': mem_apos_alertas,
            'delta': mem_apos_alertas - mem_inicial
        }
        
        return mem_inicial
    
    def test_stress_1000_alertas(self):
        """Teste 2: Stress com 1.000 alertas"""
        print("\n" + "="*70)
        print("TESTE 2: Stress - 1.000 Alertas")
        print("="*70)
        
        mem_inicial = get_memory_usage()
        
        # Criar gerenciador
        gerenciador = GerenciadorAlertas()
        
        # Gerar 1.000 alertas
        print("  Gerando 1.000 alertas...", end=" ")
        
        tipos = [TipoAlerta.CRITICO, TipoAlerta.ALTO, TipoAlerta.MEDIO, TipoAlerta.BAIXO, TipoAlerta.INFO]
        categorias = [CategoriaAlerta.CONTROLE, CategoriaAlerta.REGRA, CategoriaAlerta.EQUIPAMENTO, 
                      CategoriaAlerta.SISTEMA, CategoriaAlerta.QUALIDADE]
        
        for i in range(1000):
            tipo = random.choice(tipos)
            categoria = random.choice(categorias)
            alerta = Alerta(
                tipo, 
                categoria, 
                f"Mensagem de teste stress {i}",
                exame=f"Exame_{i % 100}",
                equipamento=random.choice(['VR1e2', 'Bio7500', 'CFXII']),
                detalhes=f"Detalhes do alerta de stress número {i}"
            )
            gerenciador.adicionar_alerta(alerta)
        
        print(f"✓ {len(gerenciador.alertas)} alertas criados")
        
        mem_apos = get_memory_usage()
        
        if mem_inicial and mem_apos:
            print(f"  Memória inicial: {mem_inicial:.2f} MB")
            print(f"  Memória final: {mem_apos:.2f} MB")
            print(f"  Delta: +{(mem_apos - mem_inicial):.2f} MB")
            print(f"  Por alerta: ~{((mem_apos - mem_inicial) / 1000):.4f} MB")
        
        # Testar operações
        print("\n  Testando operações:")
        
        # Filtragem
        print("    - Filtragem por tipo...", end=" ")
        criticos = gerenciador.get_alertas_por_tipo(TipoAlerta.CRITICO)
        print(f"✓ {len(criticos)} críticos")
        
        # Não lidos
        print("    - Contagem não lidos...", end=" ")
        nao_lidos = gerenciador.get_alertas_nao_lidos()
        print(f"✓ {len(nao_lidos)} não lidos")
        
        # Estatísticas
        print("    - Estatísticas...", end=" ")
        stats = gerenciador.get_estatisticas()
        print(f"✓ {stats['total']} total")
        
        # Meta: < 50MB para 1000 alertas
        if mem_inicial and mem_apos:
            delta_mb = mem_apos - mem_inicial
            status = "✅ PASSOU" if delta_mb < 50 else "⚠️ ATENÇÃO" if delta_mb < 100 else "❌ FALHOU"
            print(f"\n  Meta: < 50MB → {status}")
            
            self.resultados['stress_1000'] = {
                'mem_inicial': mem_inicial,
                'mem_final': mem_apos,
                'delta': delta_mb,
                'meta': 50,
                'passou': delta_mb < 50
            }
        
        return gerenciador
    
    def test_stress_10000_alertas(self):
        """Teste 3: Stress extremo com 10.000 alertas"""
        print("\n" + "="*70)
        print("TESTE 3: Stress Extremo - 10.000 Alertas")
        print("="*70)
        
        mem_inicial = get_memory_usage()
        
        # Criar gerenciador
        gerenciador = GerenciadorAlertas()
        
        # Gerar 10.000 alertas
        print("  Gerando 10.000 alertas...", end=" ")
        
        tipos = [TipoAlerta.CRITICO, TipoAlerta.ALTO, TipoAlerta.MEDIO, TipoAlerta.BAIXO, TipoAlerta.INFO]
        categorias = [CategoriaAlerta.CONTROLE, CategoriaAlerta.REGRA, CategoriaAlerta.EQUIPAMENTO, 
                      CategoriaAlerta.SISTEMA, CategoriaAlerta.QUALIDADE]
        
        for i in range(10000):
            tipo = random.choice(tipos)
            categoria = random.choice(categorias)
            alerta = Alerta(
                tipo, 
                categoria, 
                f"Stress extremo {i}",
                exame=f"Exame_{i % 500}",
                equipamento=random.choice(['VR1e2', 'Bio7500', 'CFXII', 'Quant5'])
            )
            gerenciador.adicionar_alerta(alerta)
            
            # Progresso a cada 2000
            if (i + 1) % 2000 == 0:
                print(f"{i+1}...", end=" ")
        
        print(f"✓ {len(gerenciador.alertas)} alertas criados")
        
        mem_apos = get_memory_usage()
        
        if mem_inicial and mem_apos:
            print(f"  Memória inicial: {mem_inicial:.2f} MB")
            print(f"  Memória final: {mem_apos:.2f} MB")
            print(f"  Delta: +{(mem_apos - mem_inicial):.2f} MB")
            print(f"  Por alerta: ~{((mem_apos - mem_inicial) / 10000):.4f} MB")
        
        # Testar operações
        print("\n  Testando operações:")
        
        import time
        
        # Filtragem por tipo
        inicio = time.perf_counter()
        criticos = gerenciador.get_alertas_por_tipo(TipoAlerta.CRITICO)
        tempo_tipo = (time.perf_counter() - inicio) * 1000
        print(f"    - Filtragem por tipo: {tempo_tipo:.2f}ms ({len(criticos)} resultados)")
        
        # Filtragem por categoria
        inicio = time.perf_counter()
        controle = gerenciador.get_alertas_por_categoria(CategoriaAlerta.CONTROLE)
        tempo_cat = (time.perf_counter() - inicio) * 1000
        print(f"    - Filtragem por categoria: {tempo_cat:.2f}ms ({len(controle)} resultados)")
        
        # Não lidos
        inicio = time.perf_counter()
        nao_lidos = gerenciador.get_alertas_nao_lidos()
        tempo_nao_lidos = (time.perf_counter() - inicio) * 1000
        print(f"    - Não lidos: {tempo_nao_lidos:.2f}ms ({len(nao_lidos)} resultados)")
        
        # Estatísticas
        inicio = time.perf_counter()
        stats = gerenciador.get_estatisticas()
        tempo_stats = (time.perf_counter() - inicio) * 1000
        print(f"    - Estatísticas: {tempo_stats:.2f}ms")
        
        tempo_medio = (tempo_tipo + tempo_cat + tempo_nao_lidos + tempo_stats) / 4
        
        print(f"\n  Tempo médio de operações: {tempo_medio:.2f}ms")
        
        # Meta: < 200MB para 10000 alertas
        if mem_inicial and mem_apos:
            delta_mb = mem_apos - mem_inicial
            status = "✅ PASSOU" if delta_mb < 200 else "⚠️ ATENÇÃO" if delta_mb < 500 else "❌ FALHOU"
            print(f"  Meta memória: < 200MB → {status}")
            
            # Meta: operações < 100ms
            status_tempo = "✅ PASSOU" if tempo_medio < 100 else "⚠️ ATENÇÃO" if tempo_medio < 500 else "❌ FALHOU"
            print(f"  Meta tempo: < 100ms → {status_tempo}")
            
            self.resultados['stress_10000'] = {
                'mem_inicial': mem_inicial,
                'mem_final': mem_apos,
                'delta': delta_mb,
                'tempo_medio': tempo_medio,
                'meta_mem': 200,
                'meta_tempo': 100,
                'passou': delta_mb < 200 and tempo_medio < 100
            }
        
        return gerenciador
    
    def test_memory_leak_callbacks(self):
        """Teste 4: Verificar memory leaks em callbacks"""
        print("\n" + "="*70)
        print("TESTE 4: Detecção de Memory Leaks (Callbacks)")
        print("="*70)
        
        mem_inicial = get_memory_usage()
        
        if mem_inicial is None:
            print("  ⚠️ psutil não disponível - pulando teste")
            return None
        
        gerenciador = GerenciadorAlertas()
        
        # Registrar e desregistrar callbacks múltiplas vezes
        print("  Testando ciclo de callbacks (1000 iterações)...")
        
        callbacks = []
        for i in range(1000):
            def callback():
                pass
            callbacks.append(callback)
            gerenciador.registrar_callback(callback)
            
            # A cada 200 iterações, limpar
            if (i + 1) % 200 == 0:
                gerenciador.callbacks.clear()
                callbacks.clear()
                gc.collect()
                print(f"    Iteração {i+1}: callbacks limpos")
        
        mem_final = get_memory_usage()
        
        print(f"\n  Memória inicial: {mem_inicial:.2f} MB")
        print(f"  Memória final: {mem_final:.2f} MB")
        print(f"  Delta: {(mem_final - mem_inicial):+.2f} MB")
        
        # Meta: delta < 10MB (tolerância para variações)
        delta = mem_final - mem_inicial
        status = "✅ SEM LEAKS" if abs(delta) < 10 else "⚠️ POSSÍVEL LEAK"
        print(f"\n  Status: {status}")
        
        self.resultados['memory_leak'] = {
            'mem_inicial': mem_inicial,
            'mem_final': mem_final,
            'delta': delta,
            'leak_detectado': abs(delta) >= 10
        }
        
        return not (abs(delta) >= 10)
    
    def gerar_relatorio(self):
        """Gera relatório final"""
        print("\n" + "="*70)
        print("RELATÓRIO FINAL - MEMÓRIA E STRESS")
        print("="*70)
        
        print("\n📊 RESUMO DOS TESTES:\n")
        
        # Baseline
        if 'memoria_baseline' in self.resultados:
            baseline = self.resultados['memoria_baseline']
            print(f"  📌 Baseline:")
            print(f"     Memória inicial: {baseline['inicial']:.2f} MB")
            print(f"     Delta 8 alertas: +{baseline['delta']:.2f} MB")
            print()
        
        # Stress 1000
        if 'stress_1000' in self.resultados:
            stress = self.resultados['stress_1000']
            status = "✅" if stress['passou'] else "❌"
            print(f"  {status} Stress 1.000 alertas:")
            print(f"     Delta memória: +{stress['delta']:.2f} MB | Meta: < 50MB")
            print()
        
        # Stress 10000
        if 'stress_10000' in self.resultados:
            stress = self.resultados['stress_10000']
            status = "✅" if stress['passou'] else "❌"
            print(f"  {status} Stress 10.000 alertas:")
            print(f"     Delta memória: +{stress['delta']:.2f} MB | Meta: < 200MB")
            print(f"     Tempo médio ops: {stress['tempo_medio']:.2f}ms | Meta: < 100ms")
            print()
        
        # Memory leaks
        if 'memory_leak' in self.resultados:
            leak = self.resultados['memory_leak']
            status = "✅" if not leak['leak_detectado'] else "⚠️"
            print(f"  {status} Memory Leaks:")
            print(f"     Delta callbacks: {leak['delta']:+.2f} MB")
            if leak['leak_detectado']:
                print(f"     ⚠️ Possível memory leak detectado")
            else:
                print(f"     ✅ Nenhum leak significativo detectado")
            print()
        
        # Cálculo de taxa de sucesso
        testes_com_meta = [r for r in self.resultados.values() if 'passou' in r]
        if testes_com_meta:
            passou = sum(1 for r in testes_com_meta if r['passou'])
            total = len(testes_com_meta)
            percentual = (passou / total * 100)
            print(f"📈 TAXA DE SUCESSO: {passou}/{total} ({percentual:.1f}%)")
        
        # Verifica leaks
        if 'memory_leak' in self.resultados and not self.resultados['memory_leak']['leak_detectado']:
            print("🔒 Sistema estável sem memory leaks")
        
        print("\n" + "="*70)


def executar_suite_memoria_stress():
    """Executa suite completa de testes de memória e stress"""
    print("\n" + "="*70)
    print("SUITE DE TESTES - MEMÓRIA E STRESS")
    print("="*70)
    print("\n🎯 Objetivo: Validar estabilidade com grandes volumes")
    print("📊 Volumes:")
    print("   - 1.000 alertas")
    print("   - 10.000 alertas")
    print("   - 1.000 ciclos de callbacks")
    print()
    
    tester = TestMemoriaStress()
    
    try:
        # Executar testes
        tester.test_memoria_baseline()
        tester.test_stress_1000_alertas()
        tester.test_stress_10000_alertas()
        tester.test_memory_leak_callbacks()
        
        # Gerar relatório
        tester.gerar_relatorio()
        
        return tester.resultados
        
    except Exception as e:
        print(f"\n❌ Erro durante testes: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    resultados = executar_suite_memoria_stress()
    
    # Exit code
    if resultados:
        testes_com_meta = [r for r in resultados.values() if 'passou' in r]
        if testes_com_meta:
            passou = sum(1 for r in testes_com_meta if r['passou'])
            total = len(testes_com_meta)
            sys.exit(0 if passou == total else 1)
        else:
            sys.exit(0)
    else:
        sys.exit(1)
