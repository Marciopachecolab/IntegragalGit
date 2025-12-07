"""
ExamRegistry híbrido: consolida metadados de exames a partir dos CSVs da pasta
`banco/` e, quando houver, sobrescreve/complementa com arquivos JSON/YAML em
`config/exams/`.

Campos expostos por exame (ExamConfig):
    nome_exame, slug, equipamento,
    tipo_placa_analitica, esquema_agrupamento, kit_codigo,
    alvos, mapa_alvos, faixas_ct, rps,
    export_fields, panel_tests_id, controles,
    comentarios, versao_protocolo.

Regras de merge:
    - Carrega todos os exames dos CSVs (base mínima).
    - Se existir JSON/YAML em config/exams/ com o mesmo nome_exame/slug, ele
      sobrescreve/complementa os dados do CSV.
    - Helpers para normalizar target_name e descobrir o tamanho de bloco a partir
      do esquema_agrupamento (ex.: 96->48 => bloco 2; 96->36 => bloco 3).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml  # type: ignore
    HAS_YAML = True
except Exception:
    HAS_YAML = False

BASE_DIR = Path(__file__).resolve().parent.parent
BANCO_DIR = BASE_DIR / "banco"
EXAMS_DIR = BASE_DIR / "config" / "exams"


def _norm_exame(nome: str) -> str:
    """Normaliza nome do exame: lowercase, remove acentos, strip"""
    import unicodedata
    
    # Strip e lowercase
    normalized = str(nome).strip().lower()
    
    # Remover acentos (NFKD + ASCII)
    normalized = unicodedata.normalize('NFKD', normalized)
    normalized = normalized.encode('ASCII', 'ignore').decode('ASCII')
    
    return normalized


def _safe_float(val: Any, default: float) -> float:
    try:
        return float(val)
    except Exception:
        return default


@dataclass
class ExamConfig:
    nome_exame: str
    slug: str
    equipamento: str
    tipo_placa_analitica: str
    esquema_agrupamento: str
    kit_codigo: Any
    alvos: List[str] = field(default_factory=list)
    mapa_alvos: Dict[str, str] = field(default_factory=dict)
    faixas_ct: Dict[str, float] = field(default_factory=dict)
    rps: List[str] = field(default_factory=list)
    export_fields: List[str] = field(default_factory=list)
    panel_tests_id: str = ""
    controles: Dict[str, List[str]] = field(default_factory=lambda: {"cn": [], "cp": []})
    comentarios: str = ""
    versao_protocolo: str = ""

    def normalize_target(self, name: str) -> str:
        s = str(name).strip().upper().replace("_", " ").replace("-", " ")
        # aplica mapa_alvos se existir chave normalizada
        for k, v in self.mapa_alvos.items():
            if s == str(k).strip().upper().replace("_", " ").replace("-", " "):
                return str(v).strip()
        return s

    def bloco_size(self) -> int:
        try:
            parts = self.esquema_agrupamento.split("->")
            if len(parts) == 2:
                orig = int(parts[0])
                dest = int(parts[1])
                if orig and dest:
                    return max(1, orig // dest)
        except Exception:
            pass
        return 1


class ExamRegistry:
    def __init__(self) -> None:
        self.exams: Dict[str, ExamConfig] = {}

    def load(self) -> None:
        # Limpar cache anterior
        self.exams.clear()
        
        csv_base = self._load_from_csv()
        json_override = self._load_from_json()

        # aplica override/merge
        for key, cfg in csv_base.items():
            if key in json_override:
                self.exams[key] = self._merge_configs(cfg, json_override[key])
            else:
                self.exams[key] = cfg
        # exames somente em JSON (sem CSV)
        for key, cfg in json_override.items():
            if key not in self.exams:
                self.exams[key] = cfg

    def get(self, nome_exame: str) -> Optional[ExamConfig]:
        return self.exams.get(_norm_exame(nome_exame))

    # ------------------------------------------------------------------ #
    # Carregamento dos CSVs                                              #
    # ------------------------------------------------------------------ #
    def _load_from_csv(self) -> Dict[str, ExamConfig]:
        exams: Dict[str, ExamConfig] = {}
        cfg_rows = self._read_csv(BANCO_DIR / "exames_config.csv")
        meta_rows = self._read_csv(BANCO_DIR / "exames_metadata.csv")
        regras_rows = self._read_csv(BANCO_DIR / "regras_analise_metadata.csv")

        meta_idx = {_norm_exame(r.get("exame", "")): r for r in meta_rows}
        regras_idx = {_norm_exame(r.get("exame", "")): r for r in regras_rows}

        for row in cfg_rows:
            nome = row.get("exame", "")
            key = _norm_exame(nome)
            meta = meta_idx.get(key, {})
            regras = regras_idx.get(key, {})

            tipo_placa = str(row.get("tipo_placa", meta.get("tipo_placa", ""))).strip()
            equipamento = str(row.get("equipamento", meta.get("equipamento", ""))).strip()
            kit_codigo = row.get("numero_kit", meta.get("numero_kit", ""))

            alvos = []
            mapa_alvos = {}
            faixas_ct = {}
            rps = []
            export_fields = []
            panel_tests_id = ""
            controles = {"cn": [], "cp": []}

            alvos_str = regras.get("alvos", "")
            if alvos_str:
                alvos = [a.strip() for a in str(alvos_str).split(";") if a.strip()]
            faixas_ct = {
                "detect_max": _safe_float(regras.get("CT_DETECTAVEL_MAX", 38.0), 38.0),
                "inconc_min": _safe_float(regras.get("CT_INCONCLUSIVO_MIN", 38.01), 38.01),
                "inconc_max": _safe_float(regras.get("CT_INCONCLUSIVO_MAX", 40.0), 40.0),
                "rp_min": _safe_float(regras.get("CT_RP_MIN", 15.0), 15.0),
                "rp_max": _safe_float(regras.get("CT_RP_MAX", 35.0), 35.0),
            }

            cfg = ExamConfig(
                nome_exame=nome,
                slug=_norm_exame(nome).replace(" ", "_"),
                equipamento=equipamento,
                tipo_placa_analitica=tipo_placa,
                esquema_agrupamento="",
                kit_codigo=kit_codigo,
                alvos=alvos,
                mapa_alvos=mapa_alvos,
                faixas_ct=faixas_ct,
                rps=rps,
                export_fields=export_fields,
                panel_tests_id=panel_tests_id,
                controles=controles,
            )
            exams[key] = cfg

        return exams

    # ------------------------------------------------------------------ #
    # Carregamento dos JSON/YAML                                         #
    # ------------------------------------------------------------------ #
    def _load_from_json(self) -> Dict[str, ExamConfig]:
        exams: Dict[str, ExamConfig] = {}
        if not EXAMS_DIR.exists():
            return exams

        for path in EXAMS_DIR.iterdir():
            if path.name.startswith(("schema", "template")):
                continue
            if path.suffix.lower() not in (".json", ".yaml", ".yml"):
                continue
            data = self._read_structured(path)
            if not data:
                continue
            nome = data.get("nome_exame") or data.get("exame") or path.stem
            key = _norm_exame(nome)
            cfg = ExamConfig(
                nome_exame=nome,
                slug=data.get("slug", key),
                equipamento=str(data.get("equipamento", "")).strip(),
                tipo_placa_analitica=str(data.get("tipo_placa_analitica", "")).strip(),
                esquema_agrupamento=str(data.get("esquema_agrupamento", "")).strip(),
                kit_codigo=data.get("kit_codigo", ""),
                alvos=data.get("alvos", []) or [],
                mapa_alvos=data.get("mapa_alvos", {}) or {},
                faixas_ct=data.get("faixas_ct", {}) or {},
                rps=data.get("rps", []) or [],
                export_fields=data.get("export_fields", []) or [],
                panel_tests_id=str(data.get("panel_tests_id", "")).strip(),
                controles=data.get("controles", {}) or {"cn": [], "cp": []},
                comentarios=data.get("comentarios", ""),
                versao_protocolo=data.get("versao_protocolo", ""),
            )
            exams[key] = cfg
        return exams

    # ------------------------------------------------------------------ #
    # Merge CSV + JSON                                                   #
    # ------------------------------------------------------------------ #
    def _merge_configs(self, base: ExamConfig, override: ExamConfig) -> ExamConfig:
        def pick(o: Any, b: Any) -> Any:
            return o if o not in (None, "", [], {}) else b

        merged = ExamConfig(
            nome_exame=pick(override.nome_exame, base.nome_exame),
            slug=pick(override.slug, base.slug),
            equipamento=pick(override.equipamento, base.equipamento),
            tipo_placa_analitica=pick(override.tipo_placa_analitica, base.tipo_placa_analitica),
            esquema_agrupamento=pick(override.esquema_agrupamento, base.esquema_agrupamento),
            kit_codigo=pick(override.kit_codigo, base.kit_codigo),
            alvos=pick(override.alvos, base.alvos),
            mapa_alvos={**base.mapa_alvos, **(override.mapa_alvos or {})},
            faixas_ct={**base.faixas_ct, **(override.faixas_ct or {})},
            rps=pick(override.rps, base.rps),
            export_fields=pick(override.export_fields, base.export_fields),
            panel_tests_id=pick(override.panel_tests_id, base.panel_tests_id),
            controles=pick(override.controles, base.controles),
            comentarios=pick(override.comentarios, base.comentarios),
            versao_protocolo=pick(override.versao_protocolo, base.versao_protocolo),
        )

        if not merged.esquema_agrupamento:
            blocos = {"48": "96->48", "36": "96->36", "96": "96->96"}
            merged.esquema_agrupamento = blocos.get(merged.tipo_placa_analitica, "")
        return merged

    # ------------------------------------------------------------------ #
    # Utilidades de leitura                                              #
    # ------------------------------------------------------------------ #
    def _read_csv(self, path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        import csv

        with path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [dict(row) for row in reader]

    def _read_structured(self, path: Path) -> Dict[str, Any]:
        try:
            if path.suffix.lower() == ".json":
                return json.loads(path.read_text(encoding="utf-8"))
            if path.suffix.lower() in (".yaml", ".yml") and HAS_YAML:
                return yaml.safe_load(path.read_text(encoding="utf-8"))  # type: ignore
        except Exception:
            return {}
        return {}


# Instância global simples (opcional)
registry = ExamRegistry()
try:
    registry.load()
except Exception:
    pass


def get_exam_cfg(nome_exame: str) -> ExamConfig:
    """
    Helper seguro: obtém ExamConfig do registry; se não existir, devolve um
    ExamConfig mínimo para não quebrar consumidores.
    """
    cfg = registry.get(nome_exame)
    if cfg:
        return cfg
    key = _norm_exame(nome_exame)
    return ExamConfig(
        nome_exame=nome_exame,
        slug=key.replace(" ", "_"),
        equipamento="",
        tipo_placa_analitica="96",
        esquema_agrupamento="96->96",
        kit_codigo="",
        alvos=[],
        mapa_alvos={},
        faixas_ct={"detect_max": 38.0, "inconc_min": 38.01, "inconc_max": 40.0, "rp_min": 15.0, "rp_max": 35.0},
        rps=["RP"],
        export_fields=[],
        panel_tests_id="",
        controles={"cn": [], "cp": []},
        comentarios="fallback gerado automaticamente",
        versao_protocolo="",
    )
