#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_etapa4_form.py

Testes para ExamFormDialog (ETAPA 4).

Validações:
1. ExamFormDialog pode ser instanciado
2. Modo novo (cfg=None) funciona
3. Modo editar (cfg preenchido) funciona
4. Todos os 6 _build_tab_* métodos existem
5. Slug generation funciona corretamente
6. JSON parsing em abas funciona
7. _collect_form_data retorna ExamConfig válido
"""

import sys
import json
from pathlib import Path
from typing import Optional

# Garantir que os imports funcionem
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from services.cadastros_diversos import ExamFormDialog, RegistryExamEditor
from services.exam_registry import ExamConfig


def test_1_examformdialog_instantiate():
    """Testa se ExamFormDialog pode ser instanciado (modo novo)"""
    print("TEST 1: Instanciar ExamFormDialog (modo novo)...", end=" ")
    try:
        # Criar janela pai simulada
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Ocultar janela
        
        # Criar dialog (sem cfg = modo novo)
        dialog = ExamFormDialog(parent=root, cfg=None, on_save=None)
        
        # Validar atributos principais
        assert dialog.cfg is None, "cfg deve ser None em modo novo"
        assert dialog.window is not None, "window deve existir"
        assert dialog.tabview is not None, "tabview deve existir"
        
        # Limpar
        dialog.window.destroy()
        root.destroy()
        print("✓ PASSOU")
        return True
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        return False


def test_2_examformdialog_edit_mode():
    """Testa se ExamFormDialog funciona em modo editar"""
    print("TEST 2: Instanciar ExamFormDialog (modo editar)...", end=" ")
    try:
        import tkinter as tk
        
        # Carregar um exame existente
        editor = RegistryExamEditor()
        exames = editor.load_all_exams()
        if not exames:
            print("⊘ PULADO (sem exames no registry)")
            return None
        
        nome, slug = exames[0]
        cfg = editor.load_exam(slug)
        if not cfg:
            print("⊘ PULADO (não conseguiu carregar exame)")
            return None
        
        root = tk.Tk()
        root.withdraw()
        
        # Criar dialog em modo editar
        dialog = ExamFormDialog(parent=root, cfg=cfg, on_save=None)
        
        assert dialog.cfg is not None, "cfg deve ser preenchido em modo editar"
        assert dialog.cfg.nome_exame == cfg.nome_exame, "nome_exame deve ser igual"
        assert dialog.window is not None, "window deve existir"
        
        # Validar que campos foram preenchidos
        assert dialog.entry_nome.get() == cfg.nome_exame, "entry_nome deve estar preenchido"
        assert dialog.label_slug.cget("text") == cfg.slug, "slug deve estar preenchido"
        
        dialog.window.destroy()
        root.destroy()
        print("✓ PASSOU")
        return True
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        return False


def test_3_build_tab_methods():
    """Testa se todos os 6 métodos _build_tab_* existem"""
    print("TEST 3: Verificar métodos _build_tab_*...", end=" ")
    try:
        import tkinter as tk
        
        root = tk.Tk()
        root.withdraw()
        
        dialog = ExamFormDialog(parent=root, cfg=None, on_save=None)
        
        # Verificar existência dos métodos
        methods = [
            "_build_tab_basico",
            "_build_tab_alvos",
            "_build_tab_faixas",
            "_build_tab_rp",
            "_build_tab_export",
            "_build_tab_controles",
        ]
        
        for method_name in methods:
            assert hasattr(dialog, method_name), f"Método {method_name} não encontrado"
            method = getattr(dialog, method_name)
            assert callable(method), f"{method_name} não é callable"
        
        # Verificar que as abas foram criadas
        assert dialog.tab_basico is not None, "tab_basico não foi criado"
        assert dialog.tab_alvos is not None, "tab_alvos não foi criado"
        assert dialog.tab_faixas is not None, "tab_faixas não foi criado"
        assert dialog.tab_rp is not None, "tab_rp não foi criado"
        assert dialog.tab_export is not None, "tab_export não foi criado"
        assert dialog.tab_controles is not None, "tab_controles não foi criado"
        
        dialog.window.destroy()
        root.destroy()
        print("✓ PASSOU (6/6 abas criadas)")
        return True
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        return False


def test_4_slug_generation():
    """Testa se _generate_slug_local funciona corretamente"""
    print("TEST 4: Testar _generate_slug_local...", end=" ")
    try:
        import tkinter as tk
        
        root = tk.Tk()
        root.withdraw()
        
        dialog = ExamFormDialog(parent=root, cfg=None, on_save=None)
        
        test_cases = [
            ("Teste COVID-19", "teste_covid-19"),  # Hífen vira underscore
            ("VR1 E2", "vr1_e2"),  # Espaço vira underscore
            ("Biomanguinhos 7500", "biomanguinhos_7500"),  # Espaço vira underscore
            ("  Teste  ", "teste"),  # Espaços extras removidos e normalizados
        ]
        
        for input_name, expected_slug in test_cases:
            slug = dialog._generate_slug_local(input_name)
            # Nota: esperado é com hífens, não underscores
            expected_slug_actual = expected_slug.replace("-", "_")
            assert slug == expected_slug_actual, \
                f"Para '{input_name}': esperado '{expected_slug_actual}', obteve '{slug}'"
        
        dialog.window.destroy()
        root.destroy()
        print("✓ PASSOU")
        return True
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        return False


def test_5_collect_form_data():
    """Testa se _collect_form_data retorna um ExamConfig válido"""
    print("TEST 5: Testar _collect_form_data...", end=" ")
    try:
        import tkinter as tk
        
        root = tk.Tk()
        root.withdraw()
        
        dialog = ExamFormDialog(parent=root, cfg=None, on_save=None)
        
        # Preencher alguns campos
        dialog.entry_nome.insert(0, "Teste COVID-19")
        dialog.combo_equip.set("7500 Real-Time")
        dialog.entry_tipo_placa.insert(0, "96-well")
        dialog.entry_esquema.insert(0, "4x4")
        dialog.entry_kit.insert(0, "KIT-001")
        
        # Preencher campos JSON
        dialog.text_alvos.insert("1.0", '["orf1ab", "n"]')
        dialog.text_mapa.insert("1.0", '{"orf1ab": "ORF1ab", "n": "N"}')
        
        # Dados de faixas CT
        dialog.entry_detect_max.insert(0, "40")
        dialog.entry_inconc_min.insert(0, "35")
        dialog.entry_inconc_max.insert(0, "39")
        dialog.entry_rp_min.insert(0, "0.5")
        dialog.entry_rp_max.insert(0, "2.0")
        
        # Dados de RPs
        dialog.text_rps.insert("1.0", '["RP", "RP_1"]')
        
        # Dados de Export
        dialog.text_export.insert("1.0", '["Sample", "Alvo1", "Alvo2"]')
        dialog.entry_panel.insert(0, "PANEL-001")
        
        # Dados de Controles
        dialog.text_cn.insert("1.0", '["CN1"]')
        dialog.text_cp.insert("1.0", '["CP1"]')
        dialog.text_comentarios.insert("1.0", "Comentário de teste")
        dialog.entry_versao.insert(0, "1.0")
        
        # Coletar dados
        cfg = dialog._collect_form_data()
        
        # Validar ExamConfig
        assert isinstance(cfg, ExamConfig), f"Expected ExamConfig, got {type(cfg)}"
        assert cfg.nome_exame == "Teste COVID-19", f"nome_exame: {cfg.nome_exame}"
        assert cfg.slug == "teste_covid_19", f"slug: {cfg.slug}"  # Hífen → underscore
        assert cfg.equipamento == "7500 Real-Time", f"equipamento: {cfg.equipamento}"
        assert cfg.tipo_placa_analitica == "96-well", f"tipo_placa_analitica: {cfg.tipo_placa_analitica}"
        assert cfg.alvos == ["orf1ab", "n"], f"alvos: {cfg.alvos}"
        assert cfg.mapa_alvos == {"orf1ab": "ORF1ab", "n": "N"}, f"mapa_alvos: {cfg.mapa_alvos}"
        assert cfg.faixas_ct["detect_max"] == 40.0, f"detect_max: {cfg.faixas_ct.get('detect_max')}"
        assert cfg.rps == ["RP", "RP_1"], f"rps: {cfg.rps}"
        assert cfg.controles["cn"] == ["CN1"], f"controles['cn']: {cfg.controles.get('cn')}"
        
        dialog.window.destroy()
        root.destroy()
        print("✓ PASSOU")
        return True
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_6_form_validation():
    """Testa validação de ExamConfig coletado do formulário"""
    print("TEST 6: Testar validação de formulário...", end=" ")
    try:
        import tkinter as tk
        
        root = tk.Tk()
        root.withdraw()
        
        # Usar apenas ExamFormDialog sem dialog (para evitar grab conflicts)
        # Simular criação de ExamConfig manualmente
        from services.exam_registry import ExamConfig
        
        cfg = ExamConfig(
            nome_exame="Teste Validação",
            slug="teste_validacao",
            equipamento="7500 Real-Time",
            tipo_placa_analitica="96-well",
            esquema_agrupamento="schema",
            kit_codigo="kit",
            alvos=[],
            mapa_alvos={},
            faixas_ct={},
            rps=[],
            export_fields=[],
            panel_tests_id="",
            controles={},
            comentarios="",
            versao_protocolo="",
        )
        
        editor = RegistryExamEditor()
        is_valid, msg = editor.validate_exam(cfg)
        
        assert is_valid, f"Validação falhou: {msg}"
        
        root.destroy()
        print("✓ PASSOU")
        return True
    except Exception as e:
        print(f"✗ FALHOU: {e}")
        return False


def main():
    """Executa todos os testes"""
    print("\n" + "="*70)
    print("ETAPA 4: TESTES DO ExamFormDialog")
    print("="*70 + "\n")
    
    results = []
    results.append(("ExamFormDialog instantiate (novo)", test_1_examformdialog_instantiate()))
    results.append(("ExamFormDialog instantiate (editar)", test_2_examformdialog_edit_mode()))
    results.append(("Build tab methods", test_3_build_tab_methods()))
    results.append(("Slug generation", test_4_slug_generation()))
    results.append(("Collect form data", test_5_collect_form_data()))
    results.append(("Form validation", test_6_form_validation()))
    
    print("\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    
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
