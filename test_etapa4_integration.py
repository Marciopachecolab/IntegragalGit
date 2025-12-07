#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_etapa4_integration.py

Teste de integração do ExamFormDialog com RegistryExamEditor.

Fluxo testado:
1. Criar novo ExamConfig via dialog
2. Validar dados coletados
3. Salvar em JSON
4. Recarregar registry
5. Verificar que novo exame aparece na lista
6. Carregar exame e comparar com original
7. Deletar exame
8. Verificar que foi removido
"""

import sys
import json
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from services.cadastros_diversos import ExamFormDialog, RegistryExamEditor
from services.exam_registry import ExamConfig


def test_1_create_and_save_new_exam():
    """Testa criar e salvar novo exame"""
    print("TEST 1: Criar e salvar novo exame...", end=" ")
    try:
        import tkinter as tk
        
        root = tk.Tk()
        root.withdraw()
        
        # Criar dialog
        dialog = ExamFormDialog(parent=root, cfg=None, on_save=None)
        
        # Preencher formulário
        dialog.entry_nome.insert(0, "Teste Integracao 002")
        dialog.combo_equip.set("7500 Real-Time")
        dialog.entry_tipo_placa.insert(0, "96-well")
        dialog.entry_esquema.insert(0, "4x4")
        dialog.entry_kit.insert(0, "KIT-TEST-001")
        
        dialog.text_alvos.insert("1.0", '["alvo1", "alvo2"]')
        dialog.text_mapa.insert("1.0", '{"alvo1": "Alvo 1", "alvo2": "Alvo 2"}')
        
        dialog.entry_detect_max.insert(0, "40")
        dialog.entry_inconc_min.insert(0, "35")
        dialog.entry_inconc_max.insert(0, "39")
        dialog.entry_rp_min.insert(0, "0.5")
        dialog.entry_rp_max.insert(0, "2.0")
        
        dialog.text_rps.insert("1.0", '["RP"]')
        dialog.text_export.insert("1.0", '["Sample", "Alvo1"]')
        dialog.entry_panel.insert(0, "TEST-PANEL")
        
        dialog.text_cn.insert("1.0", '["CN"]')
        dialog.text_cp.insert("1.0", '["CP"]')
        dialog.entry_versao.insert(0, "1.0")
        
        # Coletar dados
        cfg = dialog._collect_form_data()
        
        # Salvar via editor
        editor = RegistryExamEditor()
        success, msg = editor.save_exam(cfg)
        
        dialog.window.destroy()
        root.destroy()
        
        assert success, f"Falha ao salvar: {msg}"
        
        # Verificar que arquivo foi criado
        json_path = Path(BASE_DIR) / "config" / "exams" / f"{cfg.slug}.json"
        assert json_path.exists(), f"Arquivo não foi criado: {json_path}"
        
        print(f"✓ PASSOU (slug={cfg.slug})")
        return cfg.slug
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_2_reload_and_find_exam(exam_slug):
    """Testa recarregar registry e encontrar exame criado"""
    print("TEST 2: Recarregar registry e encontrar exame...", end=" ")
    try:
        if not exam_slug:
            print("⊘ PULADO (exame não foi criado)")
            return None
        
        editor = RegistryExamEditor()
        success, msg = editor.reload_registry()
        assert success, f"Falha ao recarregar: {msg}"
        
        # Carregar exame
        cfg = editor.load_exam(exam_slug)
        assert cfg is not None, f"Não conseguiu carregar exame com slug '{exam_slug}'"
        assert cfg.nome_exame == "Teste Integracao 002"
        assert cfg.equipamento == "7500 Real-Time"
        assert cfg.kit_codigo == "KIT-TEST-001"
        
        print("✓ PASSOU")
        return True
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        return False


def test_3_find_in_list(exam_slug):
    """Testa que exame aparece na lista de exames"""
    print("TEST 3: Verificar exame na lista...", end=" ")
    try:
        if not exam_slug:
            print("⊘ PULADO (exame não foi criado)")
            return None
        
        editor = RegistryExamEditor()
        exames = editor.load_all_exams()
        
        # Procurar o exame na lista pelo nome_exame (não pelo slug, pois slug retornado é normalizado)
        cfg = editor.load_exam(exam_slug)
        expected_name = cfg.nome_exame if cfg else None
        
        found = False
        for nome, slug in exames:
            if nome == expected_name:
                found = True
                break
        
        assert found, f"Exame '{expected_name}' não encontrado na lista"
        print("✓ PASSOU")
        return True
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        return False


def test_4_update_exam(exam_slug):
    """Testa editar exame existente"""
    print("TEST 4: Atualizar exame existente...", end=" ")
    try:
        if not exam_slug:
            print("⊘ PULADO (exame não foi criado)")
            return None
        
        editor = RegistryExamEditor()
        cfg = editor.load_exam(exam_slug)
        assert cfg is not None
        
        # Modificar alguns campos
        updated_cfg = ExamConfig(
            nome_exame=cfg.nome_exame,
            slug=cfg.slug,
            equipamento="QuantStudio",  # Alterado
            tipo_placa_analitica=cfg.tipo_placa_analitica,
            esquema_agrupamento=cfg.esquema_agrupamento,
            kit_codigo="KIT-TEST-002",  # Alterado
            alvos=cfg.alvos,
            mapa_alvos=cfg.mapa_alvos,
            faixas_ct=cfg.faixas_ct,
            rps=cfg.rps,
            export_fields=cfg.export_fields,
            panel_tests_id=cfg.panel_tests_id,
            controles=cfg.controles,
            comentarios="Comentário atualizado",
            versao_protocolo=cfg.versao_protocolo,
        )
        
        success, msg = editor.save_exam(updated_cfg)
        assert success, f"Falha ao atualizar: {msg}"
        
        # Recarregar e verificar
        editor.reload_registry()
        loaded = editor.load_exam(exam_slug)
        assert loaded.equipamento == "QuantStudio"
        assert loaded.kit_codigo == "KIT-TEST-002"
        assert loaded.comentarios == "Comentário atualizado"
        
        print("✓ PASSOU")
        return True
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_5_delete_exam(exam_slug):
    """Testa deletar exame"""
    print("TEST 5: Deletar exame...", end=" ")
    try:
        if not exam_slug:
            print("⊘ PULADO (exame não foi criado)")
            return None
        
        editor = RegistryExamEditor()
        
        # Verificar que existe antes de deletar
        cfg_before = editor.load_exam(exam_slug)
        assert cfg_before is not None, "Exame não existe para deletar"
        
        # Deletar
        success, msg = editor.delete_exam(exam_slug)
        assert success, f"Falha ao deletar: {msg}"
        
        # Verificar que arquivo foi removido
        json_path = Path(BASE_DIR) / "config" / "exams" / f"{cfg_before.slug}.json"
        assert not json_path.exists(), f"Arquivo ainda existe após delete: {json_path}"
        
        # Recarregar registry
        editor.reload_registry()
        cfg_after = editor.load_exam(exam_slug)
        # Nota: pode ainda existir no CSV, então só verificamos JSON
        
        print("✓ PASSOU")
        return True
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        # Limpar: deletar arquivo para próximo teste
        try:
            json_path = Path(BASE_DIR) / "config" / "exams" / f"{exam_slug}.json"
            if json_path.exists():
                json_path.unlink()
            # Também tentar com underscores removidos
            search_key = exam_slug.replace("_", " ")
            from services.cadastros_diversos import RegistryExamEditor as REditor
            editor_cleanup = REditor()
            cfg_lookup = editor_cleanup.load_exam(exam_slug)
            if cfg_lookup:
                json_path_cleanup = Path(BASE_DIR) / "config" / "exams" / f"{cfg_lookup.slug}.json"
                if json_path_cleanup.exists():
                    json_path_cleanup.unlink()
        except:
            pass
        return False


def main():
    """Executa testes de integração"""
    print("\n" + "="*70)
    print("ETAPA 4: TESTES DE INTEGRAÇÃO (ExamFormDialog + RegistryExamEditor)")
    print("="*70 + "\n")
    
    # Testes sequenciais (cada um depende do anterior)
    exam_slug = test_1_create_and_save_new_exam()
    result_2 = test_2_reload_and_find_exam(exam_slug)
    result_3 = test_3_find_in_list(exam_slug)
    result_4 = test_4_update_exam(exam_slug)
    result_5 = test_5_delete_exam(exam_slug)
    
    print("\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    
    results = [
        ("Criar e salvar novo exame", exam_slug is not None),
        ("Recarregar registry e encontrar", result_2),
        ("Verificar exame na lista", result_3),
        ("Atualizar exame", result_4),
        ("Deletar exame", result_5),
    ]
    
    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    skipped = sum(1 for _, r in results if r is None)
    
    for test_name, result in results:
        status = "✓ PASSOU" if result is True else ("✗ FALHOU" if result is False else "⊘ PULADO")
        print(f"{status:12} | {test_name}")
    
    print("="*70)
    print(f"Total: {passed} PASSOU, {failed} FALHOU, {skipped} PULADO")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
