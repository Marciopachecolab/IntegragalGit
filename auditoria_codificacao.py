#!/usr/bin/env python3
"""
Auditoria de codificação: detecta BOM, verifica leitura UTF-8 e sinaliza mojibake simples.

Fluxo:
1. Lista arquivos de texto (py, md, json, csv, txt) ignorando caches/.git/venv.
2. Para cada arquivo, detecta BOM e tenta ler como UTF-8 (fallback latin-1).
3. Marca como mojibake se encontrar tokens comuns quebrados (Ã, — etc.).
4. Gera resumo no stdout e salva AUDITORIA_CODIFICACAO.txt.
5. Opcional: converte arquivos com BOM ou latin-1 para UTF-8 sem BOM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


TOKENS_MOJIBAKE = [
    "á",
    "é",
    "ê",
    "ã",
    "ç",
    "É",
    "Â",
    "–",
    "—",
    """,
    "”",
    "…",
    "™¢",
]

TEXT_PATTERNS = ("*.py", "*.md", "*.json", "*.csv", "*.txt")
SKIP_PARTS = ("__pycache__", ".git", "venv", ".pytest")


@dataclass
class AuditResult:
    filepath: Path
    exists: bool = True
    encoding_detected: str | None = None
    has_bom: bool = False
    mojibake_found: bool = False
    mojibake_samples: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)


def detect_bom(filepath: Path) -> Tuple[str, bool]:
    with open(filepath, "rb") as f:
        raw = f.read(4)

    boms = {
        b"\xef\xbb\xbf": ("UTF-8-SIG", True),
        b"\xff\xfe": ("UTF-16-LE", True),
        b"\xfe\xff": ("UTF-16-BE", True),
    }
    for bom_bytes, (encoding, has_bom) in boms.items():
        if raw.startswith(bom_bytes):
            return encoding, has_bom
    return "UTF-8", False


def check_file_encoding(filepath: Path) -> AuditResult:
    result = AuditResult(filepath=filepath, exists=filepath.exists())
    if not result.exists:
        result.issues.append("Arquivo não existe")
        return result

    encoding, has_bom = detect_bom(filepath)
    result.encoding_detected = encoding
    result.has_bom = has_bom
    if has_bom:
        result.issues.append(f"BOM encontrado: {encoding}")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, "r", encoding="latin-1") as f:
                content = f.read()
                result.issues.append("Lido via latin-1 (não UTF-8)")
        except Exception as e:
            result.issues.append(f"Erro ao decodificar: {e}")
            return result

    for token in TOKENS_MOJIBAKE:
        if token in content:
            result.mojibake_found = True
            result.issues.append("Mojibake detectado")
            lines = content.splitlines()
            for i, line in enumerate(lines, 1):
                if token in line and len(result.mojibake_samples) < 3:
                    result.mojibake_samples.append(f"Linha {i}: {line[:120]}")
            break

    return result


def fix_utf8_file(filepath: Path) -> Tuple[bool, str]:
    try:
        raw = filepath.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            raw = raw[3:]
        elif raw.startswith(b"\xff\xfe"):
            raw = raw[2:]
        elif raw.startswith(b"\xfe\xff"):
            raw = raw[2:]

        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            content = raw.decode("latin-1")

        filepath.write_text(content, encoding="utf-8")
        return True, "Corrigido (UTF-8 sem BOM)"
    except Exception as e:
        return False, f"Erro ao corrigir: {e}"


def should_skip(path: Path) -> bool:
    return any(part in path.parts for part in SKIP_PARTS)


def audit_project() -> None:
    root = Path.cwd()
    relevant_files: List[Path] = []
    for pattern in TEXT_PATTERNS:
        relevant_files.extend(root.glob(pattern))
    relevant_files = [f for f in relevant_files if not should_skip(f)]

    print(f"Arquivos encontrados: {len(relevant_files)}")
    problematic: List[AuditResult] = []
    files_to_fix: List[Path] = []

    for filepath in sorted(relevant_files):
        result = check_file_encoding(filepath)
        if result.issues:
            problematic.append(result)
            if result.mojibake_found or result.has_bom or (result.encoding_detected and result.encoding_detected != "UTF-8"):
                files_to_fix.append(filepath)

    print(f"Com problemas: {len(problematic)} | Candidatos a correção: {len(files_to_fix)}")

    # Corrige candidatos
    for filepath in files_to_fix:
        ok, msg = fix_utf8_file(filepath)
        status = "OK" if ok else "ERRO"
        print(f"[{status}] {filepath} - {msg}")

    # Relatório
    report = [
        "AUDITORIA DE CODIFICAÇÃO",
        "=" * 80,
        f"Data: {datetime.now()}",
        f"Total auditado: {len(relevant_files)}",
        f"Com problemas: {len(problematic)}",
        f"Candidatos a correção: {len(files_to_fix)}",
        "",
    ]

    if problematic:
        report.append("ARQUIVOS COM PROBLEMAS:")
        report.append("-" * 80)
        for r in problematic:
            report.append(str(r.filepath))
            report.append(f"  Encoding detectado: {r.encoding_detected}")
            report.append(f"  BOM: {'Sim' if r.has_bom else 'Não'}")
            report.append(f"  Mojibake: {'Sim' if r.mojibake_found else 'Não'}")
            if r.issues:
                report.append("  Issues:")
                for issue in r.issues:
                    report.append(f"    - {issue}")
            if r.mojibake_samples:
                report.append("  Samples:")
                for sample in r.mojibake_samples:
                    report.append(f"    - {sample}")
            report.append("")
    else:
        report.append("Nenhum problema encontrado.")

    Path("AUDITORIA_CODIFICACAO.txt").write_text("\n".join(report), encoding="utf-8")
    print("Relatório salvo em AUDITORIA_CODIFICACAO.txt")


if __name__ == "__main__":
    audit_project()
