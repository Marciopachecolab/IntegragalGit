"""
Módulo de Cadastros Diversos para o IntegraGAL.

Este módulo fornece uma janela unificada para manutenção de:
- Exames (banco/exames_config.csv)
- Equipamentos (banco/equipamentos.csv)
- Placas (banco/placas.csv)
- Regras (banco/regras.csv)

O objetivo é permitir inclusão, edição e exclusão de registros
em arquivos CSV simples, mantendo compatibilidade com a
configuração já existente de exames (exames_config.csv).
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk

from services.system_paths import BASE_DIR
from services.config_service import config_service
from utils.logger import registrar_log


@dataclass
class CsvConfig:
    path: str
    headers: List[str]
    description: str
    separator: str = ","


class CadastrosDiversosWindow:
    """Janela principal para cadastros de exames, equipamentos, placas e regras."""

    def __init__(self, main_window: ctk.CTk | tk.Tk) -> None:
        self.main_window = main_window

        # Configurações de arquivos
        self.csv_configs: Dict[str, CsvConfig] = self._build_csv_configs()

        # Estado de seleção por aba
        self.current_exam_id: Optional[int] = None
        self.current_equipment_id: Optional[int] = None
        self.current_plate_id: Optional[int] = None
        self.current_rule_id: Optional[int] = None
        self.current_exam_slug: Optional[str] = None  # ← Para aba Registry

        # Criação da janela
        self.window = tk.Toplevel(self.main_window)
        self.window.title("Cadastros Diversos")
        self.window.geometry("1100x700")
        self.window.transient(self.main_window)
        self.window.grab_set()

        # Containers principais
        self._build_ui()

    # ------------------------------------------------------------------
    # Configuração de arquivos CSV
    # ------------------------------------------------------------------
    def _build_csv_configs(self) -> Dict[str, CsvConfig]:
        """Define os arquivos CSV utilizados para cada tipo de cadastro."""
        try:
            paths_cfg = config_service.get_paths()
        except Exception:
            paths_cfg = {}

        # Exames: utiliza o caminho já configurado em config.json, se existir
        exams_path = paths_cfg.get(
            "exams_catalog_csv", os.path.join(BASE_DIR, "banco", "exames_config.csv")
        )

        return {
            "exames": CsvConfig(
                path=exams_path,
                headers=[
                    "exame",
                    "modulo_analise",
                    "tipo_placa",
                    "numero_kit",
                    "equipamento",
                ],
                description="Catálogo de exames e módulos de análise.",
                separator=",",
            ),
            "equipamentos": CsvConfig(
                path=os.path.join(BASE_DIR, "banco", "equipamentos.csv"),
                headers=["nome", "modelo", "fabricante", "observacoes"],
                description="Cadastro de equipamentos disponíveis.",
                separator=",",
            ),
            "placas": CsvConfig(
                path=os.path.join(BASE_DIR, "banco", "placas.csv"),
                headers=["nome", "tipo", "num_pocos", "descricao"],
                description="Cadastro de tipos de placas.",
                separator=",",
            ),
            "regras": CsvConfig(
                path=os.path.join(BASE_DIR, "banco", "regras.csv"),
                headers=["nome_regra", "exame", "descricao", "parametros"],
                description="Cadastro de regras de interpretação/negócio.",
                separator=",",
            ),
        }

    # ------------------------------------------------------------------
    # Utilitários de CSV
    # ------------------------------------------------------------------
    def _ensure_csv(self, key: str) -> None:
        cfg = self.csv_configs[key]
        os.makedirs(os.path.dirname(cfg.path), exist_ok=True)
        if not os.path.exists(cfg.path):
            with open(cfg.path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f, delimiter=cfg.separator)
                writer.writerow(cfg.headers)
            registrar_log(
                "CadastrosDiversos",
                f"Arquivo criado: {cfg.path} ({key})",
                "INFO",
            )

    def _load_csv(self, key: str) -> List[Dict[str, str]]:
        cfg = self.csv_configs[key]
        self._ensure_csv(key)
        rows: List[Dict[str, str]] = []
        try:
            with open(cfg.path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=cfg.separator)
                for row in reader:
                    # Garante todas as colunas
                    normalized = {h: row.get(h, "").strip() for h in cfg.headers}
                    rows.append(normalized)
        except Exception as e:
            registrar_log(
                "CadastrosDiversos",
                f"Erro ao ler CSV {cfg.path}: {e}",
                "ERROR",
            )
            messagebox.showerror(
                "Erro",
                f"Erro ao ler arquivo de cadastro ({key}):\n{e}",
                parent=self.window,
            )
        return rows

    def _save_csv(self, key: str, rows: List[Dict[str, str]]) -> None:
        cfg = self.csv_configs[key]
        try:
            with open(cfg.path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=cfg.headers, delimiter=cfg.separator)
                writer.writeheader()
                for r in rows:
                    writer.writerow({h: r.get(h, "") for h in cfg.headers})
            registrar_log(
                "CadastrosDiversos",
                f"Arquivo salvo: {cfg.path} ({key}), {len(rows)} registros.",
                "INFO",
            )
        except Exception as e:
            registrar_log(
                "CadastrosDiversos",
                f"Erro ao salvar CSV {cfg.path}: {e}",
                "ERROR",
            )
            messagebox.showerror(
                "Erro",
                f"Erro ao salvar arquivo de cadastro ({key}):\n{e}",
                parent=self.window,
            )

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        title = ctk.CTkLabel(
            main_frame,
            text="Cadastros Diversos",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        title.pack(pady=(0, 10))

        subtitle = ctk.CTkLabel(
            main_frame,
            text=(
                "Módulo para manutenção de exames, equipamentos, placas e regras.\n"
                "As alterações são persistidas em arquivos CSV na pasta 'banco/'."
            ),
            font=ctk.CTkFont(size=13),
        )
        subtitle.pack(pady=(0, 15))

        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(expand=True, fill="both")

        self.tab_exames = self.tabview.add("Exames")
        self.tab_equip = self.tabview.add("Equipamentos")
        self.tab_placas = self.tabview.add("Placas")
        self.tab_regras = self.tabview.add("Regras")
        self.tab_exames_registry = self.tabview.add("Exames (Registry)")  # ← NEW

        self._build_tab_exames()
        self._build_tab_equipamentos()
        self._build_tab_placas()
        self._build_tab_regras()
        self._build_tab_exames_registry()  # ← NEW

    # ----------------------------- EXAMES -----------------------------
    def _build_tab_exames(self) -> None:
        frame = ctk.CTkFrame(self.tab_exames)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Tabela
        table_frame = ctk.CTkFrame(frame)
        table_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10))

        cols = self.csv_configs["exames"].headers
        self.tree_exames = ttk.Treeview(
            table_frame,
            columns=cols,
            show="headings",
            height=15,
        )
        for c in cols:
            self.tree_exames.heading(c, text=c)
            self.tree_exames.column(c, width=140, anchor="w")
        self.tree_exames.pack(expand=True, fill="both", padx=5, pady=5)
        self.tree_exames.bind("<<TreeviewSelect>>", self._on_select_exam)

        btn_frame = ctk.CTkFrame(table_frame)
        btn_frame.pack(fill="x", padx=5, pady=(0, 5))

        ctk.CTkButton(
            btn_frame,
            text="Novo",
            command=self._novo_exame,
            width=80,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Salvar",
            command=self._salvar_exame,
            width=80,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Excluir",
            command=self._excluir_exame,
            width=80,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Recarregar",
            command=self._carregar_exames,
            width=100,
        ).pack(side="right", padx=5)

        # Formulário
        form_frame = ctk.CTkFrame(frame)
        form_frame.grid(row=0, column=1, sticky="nsew")

        self.entry_exame = ctk.CTkEntry(form_frame, placeholder_text="Nome do exame")
        self.entry_exame.pack(fill="x", padx=5, pady=5)

        self.entry_modulo = ctk.CTkEntry(
            form_frame, placeholder_text="Módulo de análise (ex.: analise.vr1e2_biomanguinhos_7500.analisar_placa...)"
        )
        self.entry_modulo.pack(fill="x", padx=5, pady=5)

        self.entry_tipo_placa = ctk.CTkEntry(
            form_frame, placeholder_text="Tipo de placa (ex.: 48, 96)"
        )
        self.entry_tipo_placa.pack(fill="x", padx=5, pady=5)

        self.entry_numero_kit = ctk.CTkEntry(
            form_frame, placeholder_text="Número/ID do kit"
        )
        self.entry_numero_kit.pack(fill="x", padx=5, pady=5)

        self.entry_equipamento_exame = ctk.CTkEntry(
            form_frame, placeholder_text="Equipamento associado"
        )
        self.entry_equipamento_exame.pack(fill="x", padx=5, pady=5)

        self._carregar_exames()

    def _carregar_exames(self) -> None:
        rows = self._load_csv("exames")
        # limpar
        for item in self.tree_exames.get_children():
            self.tree_exames.delete(item)
        for idx, r in enumerate(rows):
            values = [
                r.get("exame", ""),
                r.get("modulo_analise", ""),
                r.get("tipo_placa", ""),
                r.get("numero_kit", ""),
                r.get("equipamento", ""),
            ]
            self.tree_exames.insert("", "end", iid=str(idx), values=values)

    def _on_select_exam(self, event=None) -> None:
        sel = self.tree_exames.selection()
        if not sel:
            return
        iid = sel[0]
        self.current_exam_id = int(iid)
        vals = self.tree_exames.item(iid, "values")
        if not vals:
            return
        self.entry_exame.delete(0, "end")
        self.entry_exame.insert(0, vals[0])
        self.entry_modulo.delete(0, "end")
        self.entry_modulo.insert(0, vals[1])
        self.entry_tipo_placa.delete(0, "end")
        self.entry_tipo_placa.insert(0, vals[2])
        self.entry_numero_kit.delete(0, "end")
        self.entry_numero_kit.insert(0, vals[3])
        self.entry_equipamento_exame.delete(0, "end")
        self.entry_equipamento_exame.insert(0, vals[4])

    def _novo_exame(self) -> None:
        self.current_exam_id = None
        for entry in [
            self.entry_exame,
            self.entry_modulo,
            self.entry_tipo_placa,
            self.entry_numero_kit,
            self.entry_equipamento_exame,
        ]:
            entry.delete(0, "end")

    def _salvar_exame(self) -> None:
        rows = self._load_csv("exames")
        dados = {
            "exame": self.entry_exame.get().strip(),
            "modulo_analise": self.entry_modulo.get().strip(),
            "tipo_placa": self.entry_tipo_placa.get().strip(),
            "numero_kit": self.entry_numero_kit.get().strip(),
            "equipamento": self.entry_equipamento_exame.get().strip(),
        }
        if not dados["exame"]:
            messagebox.showwarning(
                "Aviso", "O campo 'exame' é obrigatório.", parent=self.window
            )
            return

        if self.current_exam_id is None:
            rows.append(dados)
        else:
            if 0 <= self.current_exam_id < len(rows):
                rows[self.current_exam_id] = dados
            else:
                rows.append(dados)

        self._save_csv("exames", rows)
        self._carregar_exames()

    def _excluir_exame(self) -> None:
        if self.current_exam_id is None:
            messagebox.showinfo(
                "Informação",
                "Selecione um exame para excluir.",
                parent=self.window,
            )
            return

        if not messagebox.askyesno(
            "Confirmação",
            "Deseja realmente excluir o exame selecionado?",
            parent=self.window,
        ):
            return

        rows = self._load_csv("exames")
        if 0 <= self.current_exam_id < len(rows):
            rows.pop(self.current_exam_id)
            self._save_csv("exames", rows)
            self._carregar_exames()
            self._novo_exame()

    # -------------------------- EQUIPAMENTOS --------------------------
    def _build_tab_equipamentos(self) -> None:
        frame = ctk.CTkFrame(self.tab_equip)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        table_frame = ctk.CTkFrame(frame)
        table_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10))

        cols = self.csv_configs["equipamentos"].headers
        self.tree_equip = ttk.Treeview(
            table_frame,
            columns=cols,
            show="headings",
            height=15,
        )
        for c in cols:
            self.tree_equip.heading(c, text=c)
            self.tree_equip.column(c, width=160, anchor="w")
        self.tree_equip.pack(expand=True, fill="both", padx=5, pady=5)
        self.tree_equip.bind("<<TreeviewSelect>>", self._on_select_equip)

        btn_frame = ctk.CTkFrame(table_frame)
        btn_frame.pack(fill="x", padx=5, pady=(0, 5))

        ctk.CTkButton(
            btn_frame,
            text="Novo",
            command=self._novo_equip,
            width=80,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Salvar",
            command=self._salvar_equip,
            width=80,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Excluir",
            command=self._excluir_equip,
            width=80,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Recarregar",
            command=self._carregar_equip,
            width=100,
        ).pack(side="right", padx=5)

        form_frame = ctk.CTkFrame(frame)
        form_frame.grid(row=0, column=1, sticky="nsew")

        self.entry_equip_nome = ctk.CTkEntry(
            form_frame, placeholder_text="Nome do equipamento"
        )
        self.entry_equip_nome.pack(fill="x", padx=5, pady=5)

        self.entry_equip_modelo = ctk.CTkEntry(
            form_frame, placeholder_text="Modelo"
        )
        self.entry_equip_modelo.pack(fill="x", padx=5, pady=5)

        self.entry_equip_fabricante = ctk.CTkEntry(
            form_frame, placeholder_text="Fabricante"
        )
        self.entry_equip_fabricante.pack(fill="x", padx=5, pady=5)

        self.entry_equip_obs = ctk.CTkEntry(
            form_frame, placeholder_text="Observações"
        )
        self.entry_equip_obs.pack(fill="x", padx=5, pady=5)

        self._carregar_equip()

    def _carregar_equip(self) -> None:
        rows = self._load_csv("equipamentos")
        for item in self.tree_equip.get_children():
            self.tree_equip.delete(item)
        for idx, r in enumerate(rows):
            self.tree_equip.insert(
                "", "end", iid=str(idx), values=[
                    r.get("nome", ""),
                    r.get("modelo", ""),
                    r.get("fabricante", ""),
                    r.get("observacoes", ""),
                ]
            )

    def _on_select_equip(self, event=None) -> None:
        sel = self.tree_equip.selection()
        if not sel:
            return
        iid = sel[0]
        self.current_equipment_id = int(iid)
        vals = self.tree_equip.item(iid, "values")
        if not vals:
            return
        self.entry_equip_nome.delete(0, "end")
        self.entry_equip_nome.insert(0, vals[0])
        self.entry_equip_modelo.delete(0, "end")
        self.entry_equip_modelo.insert(0, vals[1])
        self.entry_equip_fabricante.delete(0, "end")
        self.entry_equip_fabricante.insert(0, vals[2])
        self.entry_equip_obs.delete(0, "end")
        self.entry_equip_obs.insert(0, vals[3])

    def _novo_equip(self) -> None:
        self.current_equipment_id = None
        for entry in [
            self.entry_equip_nome,
            self.entry_equip_modelo,
            self.entry_equip_fabricante,
            self.entry_equip_obs,
        ]:
            entry.delete(0, "end")

    def _salvar_equip(self) -> None:
        rows = self._load_csv("equipamentos")
        dados = {
            "nome": self.entry_equip_nome.get().strip(),
            "modelo": self.entry_equip_modelo.get().strip(),
            "fabricante": self.entry_equip_fabricante.get().strip(),
            "observacoes": self.entry_equip_obs.get().strip(),
        }
        if not dados["nome"]:
            messagebox.showwarning(
                "Aviso",
                "O campo 'nome' do equipamento é obrigatório.",
                parent=self.window,
            )
            return

        if self.current_equipment_id is None:
            rows.append(dados)
        else:
            if 0 <= self.current_equipment_id < len(rows):
                rows[self.current_equipment_id] = dados
            else:
                rows.append(dados)

        self._save_csv("equipamentos", rows)
        self._carregar_equip()

    def _excluir_equip(self) -> None:
        if self.current_equipment_id is None:
            messagebox.showinfo(
                "Informação",
                "Selecione um equipamento para excluir.",
                parent=self.window,
            )
            return

        if not messagebox.askyesno(
            "Confirmação",
            "Deseja realmente excluir o equipamento selecionado?",
            parent=self.window,
        ):
            return

        rows = self._load_csv("equipamentos")
        if 0 <= self.current_equipment_id < len(rows):
            rows.pop(self.current_equipment_id)
            self._save_csv("equipamentos", rows)
            self._carregar_equip()
            self._novo_equip()

    # ----------------------------- PLACAS -----------------------------
    def _build_tab_placas(self) -> None:
        frame = ctk.CTkFrame(self.tab_placas)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        table_frame = ctk.CTkFrame(frame)
        table_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10))

        cols = self.csv_configs["placas"].headers
        self.tree_placas = ttk.Treeview(
            table_frame,
            columns=cols,
            show="headings",
            height=15,
        )
        for c in cols:
            self.tree_placas.heading(c, text=c)
            self.tree_placas.column(c, width=140, anchor="w")
        self.tree_placas.pack(expand=True, fill="both", padx=5, pady=5)
        self.tree_placas.bind("<<TreeviewSelect>>", self._on_select_placa)

        btn_frame = ctk.CTkFrame(table_frame)
        btn_frame.pack(fill="x", padx=5, pady=(0, 5))

        ctk.CTkButton(
            btn_frame,
            text="Novo",
            command=self._novo_placa,
            width=80,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Salvar",
            command=self._salvar_placa,
            width=80,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Excluir",
            command=self._excluir_placa,
            width=80,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Recarregar",
            command=self._carregar_placas,
            width=100,
        ).pack(side="right", padx=5)

        form_frame = ctk.CTkFrame(frame)
        form_frame.grid(row=0, column=1, sticky="nsew")

        self.entry_placa_nome = ctk.CTkEntry(
            form_frame, placeholder_text="Nome da placa"
        )
        self.entry_placa_nome.pack(fill="x", padx=5, pady=5)

        self.entry_placa_tipo = ctk.CTkEntry(
            form_frame, placeholder_text="Tipo (ex.: 48, 96)"
        )
        self.entry_placa_tipo.pack(fill="x", padx=5, pady=5)

        self.entry_placa_pocos = ctk.CTkEntry(
            form_frame, placeholder_text="Número de poços"
        )
        self.entry_placa_pocos.pack(fill="x", padx=5, pady=5)

        self.entry_placa_desc = ctk.CTkEntry(
            form_frame, placeholder_text="Descrição/observações"
        )
        self.entry_placa_desc.pack(fill="x", padx=5, pady=5)

        self._carregar_placas()

    def _carregar_placas(self) -> None:
        rows = self._load_csv("placas")
        for item in self.tree_placas.get_children():
            self.tree_placas.delete(item)
        for idx, r in enumerate(rows):
            self.tree_placas.insert(
                "",
                "end",
                iid=str(idx),
                values=[
                    r.get("nome", ""),
                    r.get("tipo", ""),
                    r.get("num_pocos", ""),
                    r.get("descricao", ""),
                ],
            )

    def _on_select_placa(self, event=None) -> None:
        sel = self.tree_placas.selection()
        if not sel:
            return
        iid = sel[0]
        self.current_plate_id = int(iid)
        vals = self.tree_placas.item(iid, "values")
        if not vals:
            return
        self.entry_placa_nome.delete(0, "end")
        self.entry_placa_nome.insert(0, vals[0])
        self.entry_placa_tipo.delete(0, "end")
        self.entry_placa_tipo.insert(0, vals[1])
        self.entry_placa_pocos.delete(0, "end")
        self.entry_placa_pocos.insert(0, vals[2])
        self.entry_placa_desc.delete(0, "end")
        self.entry_placa_desc.insert(0, vals[3])

    def _novo_placa(self) -> None:
        self.current_plate_id = None
        for entry in [
            self.entry_placa_nome,
            self.entry_placa_tipo,
            self.entry_placa_pocos,
            self.entry_placa_desc,
        ]:
            entry.delete(0, "end")

    def _salvar_placa(self) -> None:
        rows = self._load_csv("placas")
        dados = {
            "nome": self.entry_placa_nome.get().strip(),
            "tipo": self.entry_placa_tipo.get().strip(),
            "num_pocos": self.entry_placa_pocos.get().strip(),
            "descricao": self.entry_placa_desc.get().strip(),
        }
        if not dados["nome"]:
            messagebox.showwarning(
                "Aviso",
                "O campo 'nome' da placa é obrigatório.",
                parent=self.window,
            )
            return

        if self.current_plate_id is None:
            rows.append(dados)
        else:
            if 0 <= self.current_plate_id < len(rows):
                rows[self.current_plate_id] = dados
            else:
                rows.append(dados)

        self._save_csv("placas", rows)
        self._carregar_placas()

    def _excluir_placa(self) -> None:
        if self.current_plate_id is None:
            messagebox.showinfo(
                "Informação",
                "Selecione uma placa para excluir.",
                parent=self.window,
            )
            return

        if not messagebox.askyesno(
            "Confirmação",
            "Deseja realmente excluir a placa selecionada?",
            parent=self.window,
        ):
            return

        rows = self._load_csv("placas")
        if 0 <= self.current_plate_id < len(rows):
            rows.pop(self.current_plate_id)
            self._save_csv("placas", rows)
            self._carregar_placas()
            self._novo_placa()

    # ------------------------------ REGRAS -----------------------------
    def _build_tab_regras(self) -> None:
        frame = ctk.CTkFrame(self.tab_regras)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        table_frame = ctk.CTkFrame(frame)
        table_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10))

        cols = self.csv_configs["regras"].headers
        self.tree_regras = ttk.Treeview(
            table_frame,
            columns=cols,
            show="headings",
            height=15,
        )
        for c in cols:
            self.tree_regras.heading(c, text=c)
            self.tree_regras.column(c, width=160, anchor="w")
        self.tree_regras.pack(expand=True, fill="both", padx=5, pady=5)
        self.tree_regras.bind("<<TreeviewSelect>>", self._on_select_regra)

        btn_frame = ctk.CTkFrame(table_frame)
        btn_frame.pack(fill="x", padx=5, pady=(0, 5))

        ctk.CTkButton(
            btn_frame,
            text="Novo",
            command=self._novo_regra,
            width=80,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Salvar",
            command=self._salvar_regra,
            width=80,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Excluir",
            command=self._excluir_regra,
            width=80,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Recarregar",
            command=self._carregar_regras,
            width=100,
        ).pack(side="right", padx=5)

        form_frame = ctk.CTkFrame(frame)
        form_frame.grid(row=0, column=1, sticky="nsew")

        self.entry_regra_nome = ctk.CTkEntry(
            form_frame, placeholder_text="Nome da regra"
        )
        self.entry_regra_nome.pack(fill="x", padx=5, pady=5)

        self.entry_regra_exame = ctk.CTkEntry(
            form_frame, placeholder_text="Exame associado (opcional)"
        )
        self.entry_regra_exame.pack(fill="x", padx=5, pady=5)

        self.entry_regra_desc = ctk.CTkEntry(
            form_frame, placeholder_text="Descrição da regra"
        )
        self.entry_regra_desc.pack(fill="x", padx=5, pady=5)

        self.entry_regra_param = ctk.CTkEntry(
            form_frame,
            placeholder_text="Parâmetros (livre, ex.: JSON ou key=value;key2=value2)",
        )
        self.entry_regra_param.pack(fill="x", padx=5, pady=5)

        self._carregar_regras()

    def _carregar_regras(self) -> None:
        rows = self._load_csv("regras")
        for item in self.tree_regras.get_children():
            self.tree_regras.delete(item)
        for idx, r in enumerate(rows):
            self.tree_regras.insert(
                "",
                "end",
                iid=str(idx),
                values=[
                    r.get("nome_regra", ""),
                    r.get("exame", ""),
                    r.get("descricao", ""),
                    r.get("parametros", ""),
                ],
            )

    def _on_select_regra(self, event=None) -> None:
        sel = self.tree_regras.selection()
        if not sel:
            return
        iid = sel[0]
        self.current_rule_id = int(iid)
        vals = self.tree_regras.item(iid, "values")
        if not vals:
            return
        self.entry_regra_nome.delete(0, "end")
        self.entry_regra_nome.insert(0, vals[0])
        self.entry_regra_exame.delete(0, "end")
        self.entry_regra_exame.insert(0, vals[1])
        self.entry_regra_desc.delete(0, "end")
        self.entry_regra_desc.insert(0, vals[2])
        self.entry_regra_param.delete(0, "end")
        self.entry_regra_param.insert(0, vals[3])

    def _novo_regra(self) -> None:
        self.current_rule_id = None
        for entry in [
            self.entry_regra_nome,
            self.entry_regra_exame,
            self.entry_regra_desc,
            self.entry_regra_param,
        ]:
            entry.delete(0, "end")

    def _salvar_regra(self) -> None:
        rows = self._load_csv("regras")
        dados = {
            "nome_regra": self.entry_regra_nome.get().strip(),
            "exame": self.entry_regra_exame.get().strip(),
            "descricao": self.entry_regra_desc.get().strip(),
            "parametros": self.entry_regra_param.get().strip(),
        }
        if not dados["nome_regra"]:
            messagebox.showwarning(
                "Aviso",
                "O campo 'nome_regra' é obrigatório.",
                parent=self.window,
            )
            return

        if self.current_rule_id is None:
            rows.append(dados)
        else:
            if 0 <= self.current_rule_id < len(rows):
                rows[self.current_rule_id] = dados
            else:
                rows.append(dados)

        self._save_csv("regras", rows)
        self._carregar_regras()

    def _excluir_regra(self) -> None:
        if self.current_rule_id is None:
            messagebox.showinfo(
                "Informação",
                "Selecione uma regra para excluir.",
                parent=self.window,
            )
            return

        if not messagebox.askyesno(
            "Confirmação",
            "Deseja realmente excluir a regra selecionada?",
            parent=self.window,
        ):
            return

        rows = self._load_csv("regras")
        if 0 <= self.current_rule_id < len(rows):
            rows.pop(self.current_rule_id)
            self._save_csv("regras", rows)
            self._carregar_regras()
            self._novo_regra()


# ============================================================================
# CLASSE: ExamFormDialog
# ============================================================================
# Dialog modal para criar/editar exames com 6 abas (Básico, Alvos, Faixas CT, 
# RP, Export, Controles). Integrado com RegistryExamEditor para validação 
# e persistência em JSON.
# ============================================================================


class ExamFormDialog:
    """
    Dialog modal para criar/editar exames do registry.
    
    Features:
    - 6 abas (Básico, Alvos, Faixas CT, RP, Export, Controles)
    - 13+ campos mapeados direto para ExamConfig
    - Validação de schema antes de salvar
    - JSON I/O automático via RegistryExamEditor
    - Callback opcional após salvar
    - Modo Novo (cfg=None) ou Editar (cfg preenchido)
    
    Args:
        parent: Janela pai (tk.Toplevel ou ctk.CTk)
        cfg (ExamConfig, optional): Configuração para editar. None para novo.
        on_save (callable, optional): Callback(cfg) após salvar com sucesso.
    """

    def __init__(self, parent, cfg=None, on_save=None) -> None:
        self.parent = parent
        self.cfg = cfg  # None = novo, ExamConfig = editar
        self.on_save = on_save
        self.editor = None  # Será inicializado após definir RegistryExamEditor

        # Carregar lista de equipamentos para dropdown
        self._equipamentos = self._load_equipamentos()

        # Criar janela
        self.window = tk.Toplevel(parent)
        title = f"Editar: {cfg.nome_exame}" if cfg else "Novo Exame"
        self.window.title(title)
        self.window.geometry("950x750")
        self.window.transient(parent)
        self.window.grab_set()

        # Widgets de entrada (preenchidos conforme modo)
        self.entry_nome = None
        self.label_slug = None
        self.combo_equip = None
        self.entry_tipo_placa = None
        self.entry_esquema = None
        self.entry_kit = None
        self.text_alvos = None
        self.text_mapa = None
        self.entry_detect_max = None
        self.entry_inconc_min = None
        self.entry_inconc_max = None
        self.entry_rp_min = None
        self.entry_rp_max = None
        self.text_rps = None
        self.text_export = None
        self.entry_panel = None
        self.text_cn = None
        self.text_cp = None
        self.text_comentarios = None
        self.entry_versao = None

        self._build_ui()

    def _load_equipamentos(self) -> List[str]:
        """Carrega lista de equipamentos disponíveis do banco/equipamentos.csv"""
        try:
            equip_path = Path(BASE_DIR) / "banco" / "equipamentos.csv"
            equipamentos = []
            if equip_path.exists():
                with open(equip_path, encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if "nome" in row:
                            equipamentos.append(row["nome"].strip())
            return sorted(equipamentos)
        except Exception:
            return ["7500 Real-Time", "QuantStudio"]  # Fallback

    def _build_ui(self) -> None:
        """Constrói interface com TabView + 6 abas + botões"""
        main = ctk.CTkFrame(self.window)
        main.pack(expand=True, fill="both", padx=10, pady=10)

        # Título
        title = ctk.CTkLabel(
            main,
            text="Cadastro de Exame",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title.pack(pady=(0, 15))

        # TabView com 6 abas
        self.tabview = ctk.CTkTabview(main)
        self.tabview.pack(expand=True, fill="both", pady=(0, 15))

        self.tab_basico = self.tabview.add("Básico")
        self.tab_alvos = self.tabview.add("Alvos")
        self.tab_faixas = self.tabview.add("Faixas CT")
        self.tab_rp = self.tabview.add("RP")
        self.tab_export = self.tabview.add("Export")
        self.tab_controles = self.tabview.add("Controles")

        self._build_tab_basico()
        self._build_tab_alvos()
        self._build_tab_faixas()
        self._build_tab_rp()
        self._build_tab_export()
        self._build_tab_controles()

        # Botões
        btn_frame = ctk.CTkFrame(main)
        btn_frame.pack(pady=(10, 0))

        btn_salvar = ctk.CTkButton(
            btn_frame,
            text="Salvar",
            command=self._salvar,
            fg_color="green",
        )
        btn_salvar.pack(side="left", padx=5)

        btn_cancelar = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.window.destroy,
            fg_color="red",
        )
        btn_cancelar.pack(side="left", padx=5)

    def _build_tab_basico(self) -> None:
        """Constrói aba BÁSICO com 6 campos"""
        frame = ctk.CTkFrame(self.tab_basico)
        frame.pack(expand=True, fill="both", padx=15, pady=15)

        # Nome Exame
        lbl = ctk.CTkLabel(frame, text="Nome do Exame *", font=ctk.CTkFont(weight="bold"))
        lbl.pack(anchor="w", pady=(0, 5))
        self.entry_nome = ctk.CTkEntry(frame, width=400)
        self.entry_nome.pack(fill="x", pady=(0, 15))
        if self.cfg:
            self.entry_nome.insert(0, self.cfg.nome_exame)

        # Slug (read-only)
        lbl = ctk.CTkLabel(frame, text="Slug (auto-gerado)", font=ctk.CTkFont(weight="bold"))
        lbl.pack(anchor="w", pady=(0, 5))
        self.label_slug = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(family="Consolas", size=12))
        self.label_slug.pack(fill="x", pady=(0, 15))
        if self.cfg:
            self.label_slug.configure(text=self.cfg.slug)
        self.entry_nome.bind("<KeyRelease>", self._update_slug)

        # Equipamento
        lbl = ctk.CTkLabel(frame, text="Equipamento *", font=ctk.CTkFont(weight="bold"))
        lbl.pack(anchor="w", pady=(0, 5))
        self.combo_equip = ctk.CTkComboBox(
            frame, values=self._equipamentos, width=400
        )
        self.combo_equip.pack(fill="x", pady=(0, 15))
        if self.cfg:
            self.combo_equip.set(self.cfg.equipamento)

        # Tipo Placa
        lbl = ctk.CTkLabel(frame, text="Tipo Placa Analítica", font=ctk.CTkFont(weight="bold"))
        lbl.pack(anchor="w", pady=(0, 5))
        self.entry_tipo_placa = ctk.CTkEntry(frame, width=200)
        self.entry_tipo_placa.pack(fill="x", pady=(0, 15))
        if self.cfg:
            self.entry_tipo_placa.insert(0, self.cfg.tipo_placa_analitica)

        # Esquema Agrupamento
        lbl = ctk.CTkLabel(frame, text="Esquema Agrupamento", font=ctk.CTkFont(weight="bold"))
        lbl.pack(anchor="w", pady=(0, 5))
        self.entry_esquema = ctk.CTkEntry(frame, width=200)
        self.entry_esquema.pack(fill="x", pady=(0, 15))
        if self.cfg:
            self.entry_esquema.insert(0, self.cfg.esquema_agrupamento)

        # Kit Código
        lbl = ctk.CTkLabel(frame, text="Kit Código", font=ctk.CTkFont(weight="bold"))
        lbl.pack(anchor="w", pady=(0, 5))
        self.entry_kit = ctk.CTkEntry(frame, width=200)
        self.entry_kit.pack(fill="x")
        if self.cfg:
            self.entry_kit.insert(0, str(self.cfg.kit_codigo))

    def _build_tab_alvos(self) -> None:
        """Constrói aba ALVOS com 2 campos (JSON)"""
        frame = ctk.CTkFrame(self.tab_alvos)
        frame.pack(expand=True, fill="both", padx=15, pady=15)

        # Alvos
        lbl = ctk.CTkLabel(
            frame,
            text="Alvos (JSON list)",
            font=ctk.CTkFont(weight="bold"),
        )
        lbl.pack(anchor="w", pady=(0, 5))
        self.text_alvos = ctk.CTkTextbox(frame, height=150)
        self.text_alvos.pack(expand=True, fill="both", pady=(0, 15))
        if self.cfg and self.cfg.alvos:
            import json
            self.text_alvos.insert("1.0", json.dumps(self.cfg.alvos, indent=2))

        # Mapa Alvos
        lbl = ctk.CTkLabel(
            frame,
            text="Mapa Alvos (JSON dict)",
            font=ctk.CTkFont(weight="bold"),
        )
        lbl.pack(anchor="w", pady=(0, 5))
        self.text_mapa = ctk.CTkTextbox(frame, height=150)
        self.text_mapa.pack(expand=True, fill="both")
        if self.cfg and self.cfg.mapa_alvos:
            import json
            self.text_mapa.insert("1.0", json.dumps(self.cfg.mapa_alvos, indent=2))

    def _build_tab_faixas(self) -> None:
        """Constrói aba FAIXAS CT com 5 campos (floats)"""
        frame = ctk.CTkFrame(self.tab_faixas)
        frame.pack(expand=True, fill="both", padx=15, pady=15)

        fields = [
            ("detect_max", "CT Detectável Max"),
            ("inconc_min", "CT Inconclusivo Min"),
            ("inconc_max", "CT Inconclusivo Max"),
            ("rp_min", "RP Min"),
            ("rp_max", "RP Max"),
        ]

        self._faixas_entries = {}
        for key, label in fields:
            lbl = ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(weight="bold"))
            lbl.pack(anchor="w", pady=(10, 5))
            entry = ctk.CTkEntry(frame, width=150)
            entry.pack(fill="x", pady=(0, 10))
            self._faixas_entries[key] = entry

            if self.cfg and self.cfg.faixas_ct and key in self.cfg.faixas_ct:
                entry.insert(0, str(self.cfg.faixas_ct[key]))

        # Atualizar refs globais
        self.entry_detect_max = self._faixas_entries.get("detect_max")
        self.entry_inconc_min = self._faixas_entries.get("inconc_min")
        self.entry_inconc_max = self._faixas_entries.get("inconc_max")
        self.entry_rp_min = self._faixas_entries.get("rp_min")
        self.entry_rp_max = self._faixas_entries.get("rp_max")

    def _build_tab_rp(self) -> None:
        """Constrói aba RP com 1 campo (JSON list)"""
        frame = ctk.CTkFrame(self.tab_rp)
        frame.pack(expand=True, fill="both", padx=15, pady=15)

        lbl = ctk.CTkLabel(
            frame,
            text="RPs (JSON list, ex: [\"RP\", \"RP_1\", \"RP_2\"])",
            font=ctk.CTkFont(weight="bold"),
        )
        lbl.pack(anchor="w", pady=(0, 5))
        self.text_rps = ctk.CTkTextbox(frame, height=300)
        self.text_rps.pack(expand=True, fill="both")
        if self.cfg and self.cfg.rps:
            import json
            self.text_rps.insert("1.0", json.dumps(self.cfg.rps, indent=2))

    def _build_tab_export(self) -> None:
        """Constrói aba EXPORT com 2 campos"""
        frame = ctk.CTkFrame(self.tab_export)
        frame.pack(expand=True, fill="both", padx=15, pady=15)

        # Export Fields
        lbl = ctk.CTkLabel(
            frame,
            text="Export Fields (JSON list)",
            font=ctk.CTkFont(weight="bold"),
        )
        lbl.pack(anchor="w", pady=(0, 5))
        self.text_export = ctk.CTkTextbox(frame, height=200)
        self.text_export.pack(expand=True, fill="both", pady=(0, 15))
        if self.cfg and self.cfg.export_fields:
            import json
            self.text_export.insert("1.0", json.dumps(self.cfg.export_fields, indent=2))

        # Panel Tests ID
        lbl = ctk.CTkLabel(
            frame,
            text="Panel Tests ID",
            font=ctk.CTkFont(weight="bold"),
        )
        lbl.pack(anchor="w", pady=(0, 5))
        self.entry_panel = ctk.CTkEntry(frame, width=200)
        self.entry_panel.pack(fill="x")
        if self.cfg:
            self.entry_panel.insert(0, self.cfg.panel_tests_id)

    def _build_tab_controles(self) -> None:
        """Constrói aba CONTROLES com CN/CP/comentarios/versao"""
        frame = ctk.CTkFrame(self.tab_controles)
        frame.pack(expand=True, fill="both", padx=15, pady=15)
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # CN (Controle Negativo)
        lbl = ctk.CTkLabel(
            frame,
            text="Controles CN (JSON list)",
            font=ctk.CTkFont(weight="bold"),
        )
        lbl.grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.text_cn = ctk.CTkTextbox(frame, height=100)
        self.text_cn.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        if self.cfg and self.cfg.controles and self.cfg.controles.get("cn"):
            import json
            self.text_cn.insert("1.0", json.dumps(self.cfg.controles["cn"], indent=2))

        # CP (Controle Positivo)
        lbl = ctk.CTkLabel(
            frame,
            text="Controles CP (JSON list)",
            font=ctk.CTkFont(weight="bold"),
        )
        lbl.grid(row=0, column=1, sticky="w", pady=(0, 5), padx=(5, 0))
        self.text_cp = ctk.CTkTextbox(frame, height=100)
        self.text_cp.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        if self.cfg and self.cfg.controles and self.cfg.controles.get("cp"):
            import json
            self.text_cp.insert("1.0", json.dumps(self.cfg.controles["cp"], indent=2))

        # Comentarios
        lbl = ctk.CTkLabel(
            frame,
            text="Comentários",
            font=ctk.CTkFont(weight="bold"),
        )
        lbl.grid(row=2, column=0, sticky="nw", pady=(15, 5))
        self.text_comentarios = ctk.CTkTextbox(frame, height=100)
        self.text_comentarios.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        if self.cfg:
            self.text_comentarios.insert("1.0", self.cfg.comentarios)

        # Versão Protocolo
        lbl = ctk.CTkLabel(
            frame,
            text="Versão Protocolo",
            font=ctk.CTkFont(weight="bold"),
        )
        lbl.grid(row=4, column=0, sticky="w", pady=(0, 5))
        self.entry_versao = ctk.CTkEntry(frame, width=150)
        self.entry_versao.grid(row=5, column=0, sticky="w")
        if self.cfg:
            self.entry_versao.insert(0, self.cfg.versao_protocolo)

    def _update_slug(self, event=None) -> None:
        """Atualiza label de slug baseado no nome_exame"""
        nome = self.entry_nome.get().strip()
        if nome:
            slug = self._generate_slug_local(nome)
            self.label_slug.configure(text=slug)

    def _generate_slug_local(self, nome_exame: str) -> str:
        """Gera slug localmente (mesmo algoritmo de RegistryExamEditor)
        
        Normaliza nome: lowercase, remove acentos, substitui espaços/hífens por underscores
        """
        import unicodedata
        
        # Lowercase e strip
        normalized = str(nome_exame).strip().lower()
        
        # Remover acentos (NFKD + ASCII)
        normalized = unicodedata.normalize('NFKD', normalized)
        normalized = normalized.encode('ASCII', 'ignore').decode('ASCII')
        
        # Substituir espaços e hífens por underscores
        slug = normalized.replace(" ", "_").replace("-", "_")
        
        return slug

    def _collect_form_data(self):
        """Coleta dados de todas as abas e retorna ExamConfig"""
        import json

        nome = self.entry_nome.get().strip()
        slug = self._generate_slug_local(nome)

        try:
            alvos = json.loads(self.text_alvos.get("1.0", "end"))
        except Exception:
            alvos = []

        try:
            mapa_alvos = json.loads(self.text_mapa.get("1.0", "end"))
        except Exception:
            mapa_alvos = {}

        try:
            faixas_ct = {
                "detect_max": float(self.entry_detect_max.get()),
                "inconc_min": float(self.entry_inconc_min.get()),
                "inconc_max": float(self.entry_inconc_max.get()),
                "rp_min": float(self.entry_rp_min.get()),
                "rp_max": float(self.entry_rp_max.get()),
            }
        except Exception:
            faixas_ct = {}

        try:
            rps = json.loads(self.text_rps.get("1.0", "end"))
        except Exception:
            rps = []

        try:
            export_fields = json.loads(self.text_export.get("1.0", "end"))
        except Exception:
            export_fields = []

        try:
            cn = json.loads(self.text_cn.get("1.0", "end"))
        except Exception:
            cn = []

        try:
            cp = json.loads(self.text_cp.get("1.0", "end"))
        except Exception:
            cp = []

        from services.exam_registry import ExamConfig

        return ExamConfig(
            nome_exame=nome,
            slug=slug,
            equipamento=self.combo_equip.get().strip(),
            tipo_placa_analitica=self.entry_tipo_placa.get().strip(),
            esquema_agrupamento=self.entry_esquema.get().strip(),
            kit_codigo=self.entry_kit.get().strip(),
            alvos=alvos,
            mapa_alvos=mapa_alvos,
            faixas_ct=faixas_ct,
            rps=rps,
            export_fields=export_fields,
            panel_tests_id=self.entry_panel.get().strip(),
            controles={"cn": cn, "cp": cp},
            comentarios=self.text_comentarios.get("1.0", "end").strip(),
            versao_protocolo=self.entry_versao.get().strip(),
        )

    def _salvar(self) -> None:
        """Coleta dados, valida, salva e fecha dialog"""
        try:
            # Inicializar editor aqui para evitar circular import
            if self.editor is None:
                from services.cadastros_diversos import RegistryExamEditor
                self.editor = RegistryExamEditor()

            cfg = self._collect_form_data()

            # Validar
            is_valid, msg = self.editor.validate_exam(cfg)
            if not is_valid:
                messagebox.showerror(
                    "Erro de Validação",
                    f"Validação falhou:\n{msg}",
                    parent=self.window,
                )
                return

            # Salvar
            success, msg = self.editor.save_exam(cfg)
            if not success:
                messagebox.showerror(
                    "Erro ao Salvar",
                    msg,
                    parent=self.window,
                )
                return

            # Recarregar registry
            self.editor.reload_registry()

            # Callback
            if self.on_save:
                self.on_save(cfg)

            # Sucesso
            messagebox.showinfo(
                "Sucesso",
                f"Exame '{cfg.nome_exame}' salvo com sucesso!",
                parent=self.window,
            )
            self.window.destroy()

        except Exception as e:
            messagebox.showerror(
                "Erro Inesperado",
                f"Erro ao salvar:\n{str(e)}",
                parent=self.window,
            )


# ============================================================================
# CLASSE: RegistryExamEditor
# ============================================================================
    # ------------------- EXAMES (REGISTRY) -------------------
    def _build_tab_exames_registry(self) -> None:
        """
        Constrói a aba "Exames (Registry)" para CRUD via RegistryExamEditor.
        """

        frame = ctk.CTkFrame(self.tab_exames_registry)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Status label
        self.status_registry = ctk.CTkLabel(frame, text="Carregando exames do registry...", font=ctk.CTkFont(size=14))
        self.status_registry.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,8))

        # Listbox de exames
        self.listbox_registry = tk.Listbox(frame, height=18, font=("Consolas", 12))
        self.listbox_registry.grid(row=1, column=0, sticky="nsew", padx=(0,10))

        # Botões
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.grid(row=1, column=1, sticky="n")
        self.btn_novo_registry = ctk.CTkButton(btn_frame, text="Novo", command=self._novo_exame_registry)
        self.btn_novo_registry.pack(fill="x", pady=2)
        self.btn_editar_registry = ctk.CTkButton(btn_frame, text="Editar", command=self._editar_exame_registry)
        self.btn_editar_registry.pack(fill="x", pady=2)
        self.btn_excluir_registry = ctk.CTkButton(btn_frame, text="Excluir", command=self._excluir_exame_registry)
        self.btn_excluir_registry.pack(fill="x", pady=2)
        self.btn_recarregar_registry = ctk.CTkButton(btn_frame, text="Recarregar", command=self._carregar_exames_registry)
        self.btn_recarregar_registry.pack(fill="x", pady=2)

        # Carregar exames do registry
        self._carregar_exames_registry()

        # Bind seleção
        self.listbox_registry.bind("<<ListboxSelect>>", self._on_select_exam_registry)

    def _carregar_exames_registry(self) -> None:
        """
        Carrega lista de exames do RegistryExamEditor e atualiza listbox.
        """
        from services.cadastros_diversos import RegistryExamEditor
        editor = RegistryExamEditor()
        exames = editor.load_all_exams()
        self.listbox_registry.delete(0, tk.END)
        for nome, slug in exames:
            self.listbox_registry.insert(tk.END, f"{nome} [{slug}]")
        self.status_registry.configure(text=f"{len(exames)} exames carregados.")

    def _on_select_exam_registry(self, event=None) -> None:
        """
        Atualiza estado ao selecionar exame na listbox.
        """
        selection = self.listbox_registry.curselection()
        if selection:
            value = self.listbox_registry.get(selection[0])
            # Extrai slug do texto "Nome [slug]"
            if "[" in value and "]" in value:
                slug = value.split("[")[-1].split("]")[0].strip()
                self.current_exam_slug = slug
                self.status_registry.configure(text=f"Selecionado: {value}")
        else:
            self.current_exam_slug = None
            self.status_registry.configure(text="Nenhum exame selecionado.")

    def _novo_exame_registry(self) -> None:
        """
        Abre dialog para criar novo exame com formulário multi-aba.
        Ao salvar, recarrega listbox automaticamente.
        """
        def on_save_callback(cfg):
            """Callback após salvar: recarrega UI"""
            self._carregar_exames_registry()
            self.status_registry.configure(text=f"Exame '{cfg.nome_exame}' criado com sucesso!")

        dialog = ExamFormDialog(
            parent=self.window,
            cfg=None,  # Modo novo
            on_save=on_save_callback
        )

    def _editar_exame_registry(self) -> None:
        """
        Abre dialog para editar exame selecionado.
        Ao salvar, recarrega listbox automaticamente.
        """
        if not self.current_exam_slug:
            self.status_registry.configure(text="Selecione um exame para editar.")
            return

        editor = RegistryExamEditor()
        cfg = editor.load_exam(self.current_exam_slug)
        if not cfg:
            self.status_registry.configure(text=f"Erro: Não foi possível carregar {self.current_exam_slug}")
            return

        def on_save_callback(updated_cfg):
            """Callback após salvar: recarrega UI"""
            self._carregar_exames_registry()
            self.status_registry.configure(text=f"Exame '{updated_cfg.nome_exame}' atualizado com sucesso!")

        dialog = ExamFormDialog(
            parent=self.window,
            cfg=cfg,  # Modo editar
            on_save=on_save_callback
        )

    def _excluir_exame_registry(self) -> None:
        """
        Exclui exame selecionado do registry.
        """
        if not self.current_exam_slug:
            self.status_registry.configure(text="Selecione um exame para excluir.")
            return
        from services.cadastros_diversos import RegistryExamEditor
        editor = RegistryExamEditor()
        success, msg = editor.delete_exam(self.current_exam_slug)
        self.status_registry.configure(text=msg)
        self._carregar_exames_registry()

    def _recarregar_registry(self) -> None:
        """
        Recarrega registry e atualiza listbox.
        """
        self._carregar_exames_registry()
# Responsável pela edição de exames integrada com o registry híbrido
# (CSV base + JSON override). Fornece métodos para:
#   - Carregar exames do registry
#   - Validar ExamConfig
#   - Salvar em JSON (config/exams/{slug}.json)
#   - Deletar exames
#   - Recarregar registry após modificações
# ============================================================================


class RegistryExamEditor:
    """
    Editor de exames integrado com registry híbrido (CSV+JSON).
    
    Responsabilidades:
    - Carregar lista de exames do registry
    - Validar ExamConfig contra schema esperado
    - Salvar novos/editados exames em JSON
    - Deletar exames (remover arquivo JSON)
    - Recarregar registry após modificações
    - Converter ExamConfig ↔ Dict (para JSON I/O)
    
    Attributes:
        registry: Instância global de ExamRegistry (carregada dinamicamente)
    """

    def __init__(self) -> None:
        """Inicializa o editor de exames."""
        from services.exam_registry import registry
        self.registry = registry

    def load_all_exams(self) -> List[tuple]:
        """
        Carrega lista de todos os exames do registry.
        
        Returns:
            List[tuple]: Lista de (nome_exame, slug) ordenada por nome.
            
        Example:
            >>> editor = RegistryExamEditor()
            >>> exames = editor.load_all_exams()
            >>> # [("VR1e2 Biomanguinhos 7500", "vr1e2_biomanguinhos_7500"), ...]
        """
        try:
            exames = []
            for slug, cfg in self.registry.exams.items():
                exames.append((cfg.nome_exame, slug))
            # Ordena por nome_exame (primeiro elemento da tupla)
            return sorted(exames, key=lambda x: x[0])
        except Exception as e:
            registrar_log("load_all_exams", f"Erro ao carregar exames: {e}", level="ERROR")
            return []

    def load_exam(self, slug_or_key: str) -> Optional:
        """
        Carrega configuração de um exame específico pelo slug.
        
        Args:
            slug_or_key (str): Pode ser:
                - Slug do arquivo (ex: "vr1e2_biomanguinhos_7500")
                - Chave normalizada (ex: "vr1e2 biomanguinhos 7500")
                - Nome do exame (ex: "VR1e2 Biomanguinhos 7500")
            
        Returns:
            ExamConfig | None: Configuração do exame ou None se não encontrado.
            
        Example:
            >>> cfg = editor.load_exam("vr1e2_biomanguinhos_7500")
            >>> if cfg:
            ...     print(cfg.nome_exame)
        """
        try:
            # Se for slug (contém underscore), converter para chave normalizada
            # slug: "teste_integracao_001" → chave: "teste integracao 001"
            if "_" in slug_or_key and " " not in slug_or_key:
                # Provavelmente é um slug, converter para formato de chave
                search_key = slug_or_key.replace("_", " ")
            else:
                # É um nome ou chave já normalizado
                search_key = slug_or_key
            
            # Tentar como chave normalizada (registry.get faz normalização)
            return self.registry.get(search_key)
        except Exception as e:
            registrar_log("load_exam", f"Erro ao carregar exame {slug_or_key}: {e}", level="ERROR")
            return None

    def validate_exam(self, cfg) -> tuple:
        """
        Valida um ExamConfig contra o schema esperado.
        
        Verificações:
        - Campos obrigatórios preenchidos (nome_exame, slug, equipamento)
        - Tipos corretos (str, list, dict, float, int)
        - Ranges válidos (faixas_ct valores positivos, etc.)
        - Formato de dados (JSON válido em campos dict/list)
        
        Args:
            cfg (ExamConfig): Configuração a validar
            
        Returns:
            Tuple[bool, str]: (is_valid, mensagem_erro_ou_ok)
            
        Example:
            >>> cfg = ExamConfig(nome_exame="VR1", ...)
            >>> is_valid, msg = editor.validate_exam(cfg)
            >>> if not is_valid:
            ...     print(f"Erro: {msg}")
        """
        # Validar nome_exame (obrigatório)
        if not cfg.nome_exame or not isinstance(cfg.nome_exame, str):
            return False, "nome_exame deve ser string não-vazia"

        # Validar slug (obrigatório)
        if not cfg.slug or not isinstance(cfg.slug, str):
            return False, "slug deve ser string não-vazia"

        # Validar equipamento (obrigatório)
        if not cfg.equipamento or not isinstance(cfg.equipamento, str):
            return False, "equipamento deve ser string não-vazia"

        # Validar tipo_placa_analitica (obrigatório)
        if not cfg.tipo_placa_analitica or not isinstance(cfg.tipo_placa_analitica, str):
            return False, "tipo_placa_analitica deve ser string não-vazia"

        # Validar esquema_agrupamento
        if not cfg.esquema_agrupamento or not isinstance(cfg.esquema_agrupamento, str):
            return False, "esquema_agrupamento deve ser string não-vazia"

        # Validar kit_codigo
        if cfg.kit_codigo is None:
            return False, "kit_codigo não pode ser None"

        # Validar alvos (deve ser lista)
        if not isinstance(cfg.alvos, list):
            return False, "alvos deve ser uma lista"

        # Validar mapa_alvos (deve ser dict)
        if not isinstance(cfg.mapa_alvos, dict):
            return False, "mapa_alvos deve ser um dicionário"

        # Validar faixas_ct (deve ser dict com floats)
        if not isinstance(cfg.faixas_ct, dict):
            return False, "faixas_ct deve ser um dicionário"

        # Verificar valores em faixas_ct (devem ser floats positivos)
        for key, value in cfg.faixas_ct.items():
            if not isinstance(value, (int, float)):
                return False, f"faixas_ct[{key}] deve ser numérico, recebido {type(value).__name__}"
            if value < 0:
                return False, f"faixas_ct[{key}] não pode ser negativo (recebido {value})"

        # Validar rps (deve ser lista)
        if not isinstance(cfg.rps, list):
            return False, "rps deve ser uma lista"

        # Validar export_fields (deve ser lista)
        if not isinstance(cfg.export_fields, list):
            return False, "export_fields deve ser uma lista"

        # Validar panel_tests_id (pode ser vazio, mas deve ser string)
        if not isinstance(cfg.panel_tests_id, str):
            return False, "panel_tests_id deve ser string"

        # Validar controles (deve ser dict)
        if not isinstance(cfg.controles, dict):
            return False, "controles deve ser um dicionário"

        # Validar estrutura de controles (cn e cp devem ser listas)
        if "cn" in cfg.controles and not isinstance(cfg.controles["cn"], list):
            return False, "controles['cn'] deve ser uma lista"
        if "cp" in cfg.controles and not isinstance(cfg.controles["cp"], list):
            return False, "controles['cp'] deve ser uma lista"

        # Validar comentarios (pode ser vazio)
        if not isinstance(cfg.comentarios, str):
            return False, "comentarios deve ser string"

        # Validar versao_protocolo (pode ser vazio)
        if not isinstance(cfg.versao_protocolo, str):
            return False, "versao_protocolo deve ser string"

        return True, "Validação OK"

    def save_exam(self, cfg) -> tuple:
        """
        Salva um ExamConfig em JSON (config/exams/{slug}.json).
        
        Processo:
        1. Valida ExamConfig
        2. Se inválido, retorna (False, mensagem_erro)
        3. Se válido, serializa para dict
        4. Salva em config/exams/{slug}.json
        5. Retorna (True, "Salvo")
        
        Args:
            cfg (ExamConfig): Configuração a salvar
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
            
        Example:
            >>> cfg = ExamConfig(nome_exame="VR1", ...)
            >>> success, msg = editor.save_exam(cfg)
            >>> if success:
            ...     print("Salvo com sucesso!")
        """
        import json
        from pathlib import Path

        # Validar antes de salvar
        is_valid, validation_msg = self.validate_exam(cfg)
        if not is_valid:
            return False, f"Validação falhou: {validation_msg}"

        try:
            # Converter ExamConfig para dict
            exam_dict = self._exam_to_dict(cfg)

            # Definir caminho de saída
            config_dir = Path(BASE_DIR) / "config" / "exams"
            config_dir.mkdir(parents=True, exist_ok=True)
            json_path = config_dir / f"{cfg.slug}.json"

            # Salvar JSON com indentação para legibilidade
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(exam_dict, f, indent=2, ensure_ascii=False)

            registrar_log("save_exam", f"Exame salvo: {json_path}", level="INFO")
            return True, f"Exame '{cfg.nome_exame}' salvo em {json_path}"

        except Exception as e:
            error_msg = f"Erro ao salvar exame: {str(e)}"
            registrar_log("save_exam", error_msg, level="ERROR")
            return False, error_msg

    def delete_exam(self, slug_or_key: str) -> tuple:
        """
        Deleta um exame removendo seu arquivo JSON.
        
        Nota: CSVs não são deletados (apenas JSONs são removidos).
        Após deletar, o exame volta à configuração do CSV (se existir).
        
        Args:
            slug_or_key (str): Slug do exame (nome arquivo) OU chave normalizada.
                               Tenta primeiro como chave normalizada do registry.
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
            
        Example:
            >>> success, msg = editor.delete_exam("vr1e2_biomanguinhos_7500")
            >>> if success:
            ...     print("Deletado!")
        """
        from pathlib import Path

        try:
            # Tentar primeiro como chave normalizada (para compatibilidade com registry.get())
            cfg = self.registry.get(slug_or_key)
            if cfg:
                # Usar o slug do ExamConfig para encontrar o arquivo
                file_slug = cfg.slug
            else:
                # Se não encontrou no registry, usar como slug direto
                file_slug = slug_or_key

            config_dir = Path(BASE_DIR) / "config" / "exams"
            json_path = config_dir / f"{file_slug}.json"

            if json_path.exists():
                json_path.unlink()
                registrar_log("delete_exam", f"Exame deletado: {json_path}", level="INFO")
                return True, "Exame deletado com sucesso"
            else:
                return False, f"Arquivo não encontrado: {json_path}"

        except Exception as e:
            error_msg = f"Erro ao deletar exame: {str(e)}"
            registrar_log("delete_exam", error_msg, level="ERROR")
            return False, error_msg

    def reload_registry(self) -> tuple:
        """
        Recarrega registry do disco (CSV + JSON).
        
        Deve ser chamado após salvar/deletar exames para sincronizar UI.
        
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
            
        Example:
            >>> # Após save_exam():
            >>> success, msg = editor.reload_registry()
            >>> if success:
            ...     print("Registry recarregado!")
        """
        try:
            self.registry.load()
            registrar_log("reload_registry", "Registry recarregado", level="INFO")
            return True, "Registry recarregado com sucesso"
        except Exception as e:
            error_msg = f"Erro ao recarregar registry: {str(e)}"
            registrar_log("reload_registry", error_msg, level="ERROR")
            return False, error_msg

    def _exam_to_dict(self, cfg) -> dict:
        """
        Converte ExamConfig para dict para serialização em JSON.
        
        Args:
            cfg (ExamConfig): Configuração a converter
            
        Returns:
            dict: Representação JSON-ready do exame
            
        Example:
            >>> exam_dict = editor._exam_to_dict(cfg)
            >>> json.dump(exam_dict, f)
        """
        return {
            "nome_exame": cfg.nome_exame,
            "slug": cfg.slug,
            "equipamento": cfg.equipamento,
            "tipo_placa_analitica": cfg.tipo_placa_analitica,
            "esquema_agrupamento": cfg.esquema_agrupamento,
            "kit_codigo": cfg.kit_codigo,
            "alvos": cfg.alvos,
            "mapa_alvos": cfg.mapa_alvos,
            "faixas_ct": cfg.faixas_ct,
            "rps": cfg.rps,
            "export_fields": cfg.export_fields,
            "panel_tests_id": cfg.panel_tests_id,
            "controles": cfg.controles,
            "comentarios": cfg.comentarios,
            "versao_protocolo": cfg.versao_protocolo,
        }

    def _generate_slug(self, nome_exame: str) -> str:
        """
        Gera slug a partir de nome_exame, garantindo correspondência com _norm_exame().
        
        Normaliza: lowercase, remove acentos, substitui espaços/hífens por underscores.
        
        Args:
            nome_exame (str): Nome do exame
            
        Returns:
            str: Slug (ex: "teste_covid_19")
            
        Example:
            >>> editor._generate_slug("Teste COVID-19")
            >>> "teste_covid_19"  # Acentos removidos, espaço e hífen → underscores
        """
        import unicodedata
        
        # Normalizar como o registry faz
        normalized = str(nome_exame).strip().lower()
        
        # Remover acentos (NFKD + ASCII)
        normalized = unicodedata.normalize('NFKD', normalized)
        normalized = normalized.encode('ASCII', 'ignore').decode('ASCII')
        
        # Substituir espaços e hífens por underscores
        slug = normalized.replace(" ", "_").replace("-", "_")
        return slug
