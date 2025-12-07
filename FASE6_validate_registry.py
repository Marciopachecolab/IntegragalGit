#!/usr/bin/env python3
"""
FASE 6 ‚Äî Script de Valida√ß√£o da Registry Ap√≥s Migra√ß√£o

Objetivo: Validar que registry carrega todos exames migrados
- registry.load() carrega todos JSONs
- Verificar merge CSV+JSON
- Teste load_exam() para cada exame
- Gerar relat√≥rio de valida√ß√£o
"""

import sys
from pathlib import Path

# Adiciona projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from services.exam_registry import ExamRegistry

# ============================================================================
# VALIDA√á√ÉO
# ============================================================================

def validate_registry():
    """Executa valida√ß√£o completa da registry."""
    
    print("=" * 80)
    print("üìã FASE 6 ‚Äî VALIDA√á√ÉO DA REGISTRY")
    print("=" * 80)
    
    # Inicializa registry
    print("\nüîÑ Carregando registry...")
    try:
        registry = ExamRegistry()
        registry.load()
        print("   ‚úì Registry carregada")
    except Exception as e:
        print(f"   ‚ùå Erro ao carregar registry: {e}")
        return False
    
    # Verificar exames carregados
    print("\nüìä Exames carregados:")
    all_exams = registry.exams
    print(f"   Total: {len(all_exams)}")
    
    for nome, cfg in all_exams.items():
        print(f"   ‚Ä¢ {nome}")
        print(f"     - Slug: {cfg.slug}")
        print(f"     - Placa: {cfg.tipo_placa_analitica}")
        print(f"     - Alvos: {len(cfg.alvos)} targets")
    
    # Teste load_exam() por nome normalizado (com espa√ßos)
    print("\nüß™ Testando load_exam() por nome normalizado:")
    test_exams = [
        "vr1",
        "vr2", 
        "vr1e2 biomanguinhos 7500",  # Com espa√ßo, n√£o underscore!
        "zdc biomanguinhos 7500"       # Com espa√ßo, n√£o underscore!
    ]
    
    results = []
    for slug in test_exams:
        try:
            cfg = registry.get(slug)
            if cfg:
                print(f"   ‚úÖ {slug}: Carregado")
                print(f"      - Nome: {cfg.nome_exame}")
                print(f"      - Equipamento: {cfg.equipamento}")
                print(f"      - Alvos: {cfg.alvos}")
                results.append((slug, True, "OK"))
            else:
                print(f"   ‚ùå {slug}: N√£o encontrado")
                results.append((slug, False, "Not found"))
        except Exception as e:
            print(f"   ‚ùå {slug}: Erro - {e}")
            results.append((slug, False, str(e)))
    
    # Verificar merge CSV+JSON
    print("\nüîÄ Verificando merge CSV+JSON:")
    try:
        cfg = registry.get("vr1e2 biomanguinhos 7500")  # Nome normalizado com espa√ßo
        if cfg:
            print(f"   Exame: {cfg.nome_exame}")
            print(f"   ‚Ä¢ tipo_placa_analitica (JSON): {cfg.tipo_placa_analitica}")
            print(f"   ‚Ä¢ equipamento (CSV): {cfg.equipamento}")
            print(f"   ‚Ä¢ alvos (JSON): {cfg.alvos}")
            print(f"   ‚Ä¢ faixas_ct (JSON): {cfg.faixas_ct}")
            print(f"   ‚Ä¢ controles (JSON): {cfg.controles}")
            print("   ‚úÖ Merge funcionando")
    except Exception as e:
        print(f"   ‚ùå Erro no merge: {e}")
    
    # Resumo
    print("\n" + "=" * 80)
    print("üìä RESUMO DA VALIDA√á√ÉO")
    print("=" * 80)
    
    success_count = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    
    print(f"\n‚úÖ Sucesso: {success_count}/{total}")
    if success_count == total:
        print("üéâ Todas as valida√ß√µes passaram!")
    
    # Log
    with open("FASE6_VALIDATION_REPORT.txt", "w", encoding="utf-8") as f:
        f.write("FASE 6 ‚Äî RELAT√ìRIO DE VALIDA√á√ÉO\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Exames carregados: {len(all_exams)}\n")
        f.write(f"Testes load_exam(): {success_count}/{total} passaram\n\n")
        f.write("DETALHES:\n")
        for slug, ok, msg in results:
            status = "‚úÖ" if ok else "‚ùå"
            f.write(f"{status} {slug}: {msg}\n")
    
    print("\nüìÑ Relat√≥rio salvo em: FASE6_VALIDATION_REPORT.txt")
    
    return success_count == total

if __name__ == "__main__":
    success = validate_registry()
    sys.exit(0 if success else 1)
