#!/usr/bin/env python3
"""
FASE 6 ‚Äî Script de Migra√ß√£o de Exames para JSON

Objetivo: Migrar exames de CSV para JSON com valida√ß√£o
- Ler banco/exames_config.csv
- Ler banco/regras_analise_metadata.csv
- Gerar config/exames/{slug}.json para cada exame
- Validar schema ExamConfig
"""

import json
import csv
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple

# ============================================================================
# CONSTANTES E TEMPLATES
# ============================================================================

# Template padr√£o para novos exames
TEMPLATE_DEFAULT = {
    "nome_exame": "DEFAULT",
    "slug": "default",
    "equipamento": "7500 Real-Time",
    "tipo_placa_analitica": "96",
    "esquema_agrupamento": "96->96",
    "kit_codigo": 0,
    "alvos": [],
    "mapa_alvos": {},
    "faixas_ct": {
        "detect_max": 38.0,
        "inconc_min": 38.01,
        "inconc_max": 40.0,
        "rp_min": 15.0,
        "rp_max": 35.0
    },
    "rps": ["RP"],
    "export_fields": [],
    "panel_tests_id": "1",
    "controles": {
        "cn": [],
        "cp": []
    },
    "comentarios": "Migrado de CSV"
}

# Mapeamento de tipo_placa ‚Üí esquema_agrupamento
PLACA_ESQUEMA = {
    "96": "96->96",
    "48": "96->48",
    "36": "96->36",
}

# Mapeamento de nome_exame ‚Üí targets+controles espec√≠ficos
EXAME_CONFIG = {
    "VR1": {
        "targets": ["VR1"],
        "alvos": ["VR1"],
        "export_fields": ["VR1"],
        "cn": ["G11+G12"],
        "cp": ["H11+H12"],
    },
    "VR2": {
        "targets": ["VR2"],
        "alvos": ["VR2"],
        "export_fields": ["VR2"],
        "cn": ["G11+G12"],
        "cp": ["H11+H12"],
    },
    "VR1e2 Biomanguinhos 7500": {
        "targets": ["SC2", "HMPV", "INF A", "INF B", "ADV", "RSV", "HRV"],
        "alvos": ["SC2", "HMPV", "INF A", "INF B", "ADV", "RSV", "HRV"],
        "export_fields": [
            "Sars-Cov-2", "Influenzaa", "influenzab", 
            "RSV", "adenov√≠rus", "metapneumovirus", "rinov√≠rus"
        ],
        "cn": ["G11+G12"],
        "cp": ["H11+H12"],
    },
    "ZDC Biomanguinhos 7500": {
        "targets": ["DEN1", "DEN2", "DEN3", "DEN4", "ZYK", "CHIK"],
        "alvos": ["DEN1", "DEN2", "DEN3", "DEN4", "ZYK", "CHIK"],
        "export_fields": [
            "Dengue1", "Dengue2", "Dengue3", "Dengue4",
            "Zika", "Chikungunya"
        ],
        "cn": ["G7+G8"],
        "cp": ["H7+H8"],
    },
}

# ============================================================================
# FUN√á√ïES AUXILIARES
# ============================================================================

def normalize_slug(nome: str) -> str:
    """Normaliza nome para slug (lowercase, sem acentos, underscores)."""
    # Remove acentos
    nfkd = unicodedata.normalize('NFKD', nome)
    slug = nfkd.encode('ASCII', 'ignore').decode('ASCII')
    # Lowercase, replace spaces/hyphens with underscores
    slug = slug.lower().strip()
    slug = slug.replace(" ", "_").replace("-", "_")
    # Remove m√∫ltiplos underscores
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug

def load_csv(filepath: str) -> List[Dict]:
    """Carrega arquivo CSV e retorna lista de dicts."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        print(f"‚ùå Erro ao ler {filepath}: {e}")
        return []

def create_exam_json(csv_row: Dict, metadata_row: Dict = None) -> Dict:
    """Cria ExamConfig JSON baseado em dados CSV."""
    nome = csv_row.get("exame", "UNKNOWN").strip()
    tipo_placa = csv_row.get("tipo_placa", "96").strip()
    equipamento = csv_row.get("equipamento", "7500 Real-Time").strip()
    kit_codigo = int(csv_row.get("numero_kit", 0))
    
    # Gera slug
    slug = normalize_slug(nome)
    
    # Cria base a partir do template
    exam = TEMPLATE_DEFAULT.copy()
    exam["nome_exame"] = nome
    exam["slug"] = slug
    exam["equipamento"] = equipamento
    exam["tipo_placa_analitica"] = tipo_placa
    exam["esquema_agrupamento"] = PLACA_ESQUEMA.get(tipo_placa, "96->96")
    exam["kit_codigo"] = kit_codigo
    
    # Aplica configura√ß√£o espec√≠fica se existir
    if nome in EXAME_CONFIG:
        cfg = EXAME_CONFIG[nome]
        exam["alvos"] = cfg.get("alvos", [])
        exam["export_fields"] = cfg.get("export_fields", [])
        exam["controles"]["cn"] = cfg.get("cn", [])
        exam["controles"]["cp"] = cfg.get("cp", [])
    else:
        # Default para exames desconhecidos
        exam["alvos"] = [nome]
        exam["export_fields"] = [nome]
        exam["controles"]["cn"] = ["G11+G12"]
        exam["controles"]["cp"] = ["H11+H12"]
    
    # Gera mapa_alvos (simples: cada alvo mapeia para si mesmo)
    exam["mapa_alvos"] = {alvo: alvo for alvo in exam["alvos"]}
    
    # Coment√°rio
    exam["comentarios"] = f"Exame {nome}; placa {tipo_placa}; migrado de CSV"
    
    return exam

def validate_exam_config(exam: Dict) -> Tuple[bool, str]:
    """Valida se ExamConfig tem os campos obrigat√≥rios."""
    required = [
        "nome_exame", "slug", "equipamento", "tipo_placa_analitica",
        "esquema_agrupamento", "kit_codigo", "alvos", "mapa_alvos",
        "faixas_ct", "rps", "export_fields", "panel_tests_id", 
        "controles", "comentarios"
    ]
    
    for field in required:
        if field not in exam:
            return False, f"Campo faltando: {field}"
    
    # Valida tipos
    if not isinstance(exam["alvos"], list):
        return False, "alvos deve ser lista"
    if not isinstance(exam["controles"], dict):
        return False, "controles deve ser dict"
    if not isinstance(exam["faixas_ct"], dict):
        return False, "faixas_ct deve ser dict"
    
    return True, "OK"

def save_exam_json(exam: Dict, output_dir: str = "config/exams") -> Tuple[bool, str]:
    """Salva ExamConfig em JSON."""
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        slug = exam["slug"]
        filepath = Path(output_dir) / f"{slug}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(exam, f, indent=2, ensure_ascii=False)
        
        return True, f"‚úÖ Salvo: {filepath}"
    except Exception as e:
        return False, f"‚ùå Erro ao salvar: {e}"

# ============================================================================
# MIGRA√á√ÉO PRINCIPAL
# ============================================================================

def migrate_all_exams():
    """Executa migra√ß√£o completa de exames."""
    
    print("=" * 80)
    print("üöÄ FASE 6 ‚Äî MIGRA√á√ÉO DE EXAMES PARA JSON")
    print("=" * 80)
    
    # Load CSVs
    print("\nüìÇ Carregando dados...")
    exames = load_csv("banco/exames_config.csv")
    metadata = load_csv("banco/regras_analise_metadata.csv")
    
    print(f"   ‚úì Exames: {len(exames)} encontrados")
    print(f"   ‚úì Regras: {len(metadata)} encontradas")
    
    if not exames:
        print("‚ùå Nenhum exame encontrado em exames_config.csv")
        return
    
    # Mapear metadata por nome
    metadata_map = {row.get("exame", "").strip(): row for row in metadata}
    
    # Migrar cada exame
    print("\nüîÑ Migrando exames...")
    results = []
    
    for i, exam_row in enumerate(exames, 1):
        nome = exam_row.get("exame", "").strip()
        if not nome:
            print(f"   ‚ö†Ô∏è  Exame {i}: nome vazio, pulando")
            continue
        
        print(f"\n   [{i}] {nome}")
        
        # Criar JSON
        exam_json = create_exam_json(exam_row, metadata_map.get(nome))
        print(f"       ‚Ä¢ Nome: {exam_json['nome_exame']}")
        print(f"       ‚Ä¢ Slug: {exam_json['slug']}")
        print(f"       ‚Ä¢ Placa: {exam_json['tipo_placa_analitica']}")
        print(f"       ‚Ä¢ Alvos: {exam_json['alvos']}")
        
        # Validar
        valid, msg = validate_exam_config(exam_json)
        if not valid:
            print(f"       ‚ùå Valida√ß√£o falhou: {msg}")
            results.append((nome, False, msg))
            continue
        print("       ‚úì Schema validado")
        
        # Salvar
        success, msg = save_exam_json(exam_json)
        if not success:
            print(f"       {msg}")
            results.append((nome, False, msg))
            continue
        print(f"       {msg}")
        results.append((nome, True, "Migrado com sucesso"))
    
    # Resumo
    print("\n" + "=" * 80)
    print("üìä RESUMO DA MIGRA√á√ÉO")
    print("=" * 80)
    
    success_count = sum(1 for _, ok, _ in results if ok)
    failed_count = len(results) - success_count
    
    print(f"\n‚úÖ Sucesso: {success_count}")
    print(f"‚ùå Falhas: {failed_count}")
    print(f"üìä Total: {len(results)}")
    
    if failed_count > 0:
        print("\n‚ö†Ô∏è  Exames com falha:")
        for nome, ok, msg in results:
            if not ok:
                print(f"   ‚Ä¢ {nome}: {msg}")
    
    # Log
    with open("FASE6_MIGRATION_LOG.txt", "w", encoding="utf-8") as f:
        f.write("FASE 6 ‚Äî LOG DE MIGRA√á√ÉO\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total processado: {len(results)}\n")
        f.write(f"Sucesso: {success_count}\n")
        f.write(f"Falha: {failed_count}\n\n")
        f.write("DETALHES:\n")
        for nome, ok, msg in results:
            status = "‚úÖ" if ok else "‚ùå"
            f.write(f"{status} {nome}: {msg}\n")
    
    print("\nüìÑ Log salvo em: FASE6_MIGRATION_LOG.txt")
    print("\n‚ú® Migra√ß√£o conclu√≠da!")

if __name__ == "__main__":
    migrate_all_exams()
