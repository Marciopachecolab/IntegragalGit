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

        self._build_tab_exames()
        self._build_tab_equipamentos()
        self._build_tab_placas()
        self._build_tab_regras()

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
