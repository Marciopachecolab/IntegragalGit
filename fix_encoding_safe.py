#!/usr/bin/env python3
"""
Safe mojibake scanner/fixer for the repository.

Behavior:
- Reads text files; tries UTF-8 first, falls back to Latin-1 on decode error.
- Detects common mojibake tokens (á, ã, é, –, —, ", ”, etc.).
- Applies a replacement map to restore accents/punctuation.
- Rewrites only when content changes; saves as UTF-8 (no BOM).

Usage:
    python fix_encoding_safe.py [root_dir]
Defaults to the directory where the script lives.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

# Replacement map: mojibake token -> correct character
MOJIBAKE_MAP: dict[str, str] = {
    # lowercase
    "\u00c3\u00a1": "\u00e1",  # á -> á
    "\u00c3\u00a2": "\u00e2",  # â -> â
    "\u00c3\u00a3": "\u00e3",  # ã -> ã
    "\u00c3\u00a4": "\u00e4",  # ä -> ä
    "\u00c3\u00a0": "\u00e0",  # à -> à
    "\u00c3\u00aa": "\u00ea",  # ê -> ê
    "\u00c3\u00a9": "\u00e9",  # é -> é
    "\u00c3\u00a8": "\u00e8",  # è -> è
    "\u00c3\u00ab": "\u00eb",  # ë -> ë
    "\u00c3\u00ae": "\u00ee",  # î -> î
    "\u00c3\u00ad": "\u00ed",  # í -> í
    "\u00c3\u00ac": "\u00ec",  # ì -> ì
    "\u00c3\u00af": "\u00ef",  # ï -> ï
    "\u00c3\u00b4": "\u00f4",  # ô -> ô
    "\u00c3\u00b3": "\u00f3",  # ó -> ó
    "\u00c3\u00b2": "\u00f2",  # ò -> ò
    "\u00c3\u00b6": "\u00f6",  # ö -> ö
    "\u00c3\u00b5": "\u00f5",  # õ -> õ
    "\u00c3\u00bc": "\u00fc",  # ü -> ü
    "\u00c3\u00ba": "\u00fa",  # ú -> ú
    "\u00c3\u00b9": "\u00f9",  # ù -> ù
    "\u00c3\u00a7": "\u00e7",  # ç -> ç
    "\u00c3\u00b1": "\u00f1",  # ñ -> ñ
    # uppercase
    "\u00c3\u0081": "\u00c1",  # Ã� -> Á
    "\u00c3\u0082": "\u00c2",  # Â -> Â
    "\u00c3\u0083": "\u00c3",  # Ã -> Ã
    "\u00c3\u0084": "\u00c4",  # Ã„ -> Ä
    "\u00c3\u0080": "\u00c0",  # À -> À
    "\u00c3\u008a": "\u00ca",  # Ê -> Ê
    "\u00c3\u0089": "\u00c9",  # É -> É
    "\u00c3\u0088": "\u00c8",  # Ãˆ -> È
    "\u00c3\u008b": "\u00cb",  # Ã‹ -> Ë
    "\u00c3\u008e": "\u00ce",  # Î -> Î
    "\u00c3\u008d": "\u00cd",  # Ã� -> Í
    "\u00c3\u008c": "\u00cc",  # ÃŒ -> Ì
    "\u00c3\u008f": "\u00cf",  # Ã� -> Ï
    "\u00c3\u0094": "\u00d4",  # Ô -> Ô
    "\u00c3\u0093": "\u00d3",  # Ó -> Ó
    "\u00c3\u0092": "\u00d2",  # Ã’ -> Ò
    "\u00c3\u0096": "\u00d6",  # Ã– -> Ö
    "\u00c3\u0095": "\u00d5",  # Õ -> Õ
    "\u00c3\u009c": "\u00dc",  # Ãœ -> Ü
    "\u00c3\u009a": "\u00da",  # Ú -> Ú
    "\u00c3\u0099": "\u00d9",  # Ã™ -> Ù
    "\u00c3\u0087": "\u00c7",  # Ç -> Ç
    "\u00c3\u0091": "\u00d1",  # Ã,
    '’':  -> Ñ
    # punctuation / symbols
    "\u00e2\u20ac\u201c": "\u2013",  # – -> –
    "\u00e2\u20ac\u201d": "\u2014",  # — -> —
    "\u00e2\u20ac\u0153": "\u201c",  # " -> "
    "\u00e2\u20ac\u009d": "\u201d",  # ™� -> ”
    "\u00e2\u20ac\u02dc": "\u2018",  # ,
    '’':  -> ,
    '’': 
    "\u00e2\u20ac\u2122": "\u2019",  # ’ -> ’
    "\u00e2\u20ac\u00a6": "\u2026",  # … -> …
    "\u00e2\u20a2": "\u00a2",        # â¢ -> ¢
    "\u00e2\u20a6": "\u20a6",       # â¦ -> ₦ (rare)
    "\u00e2\u20a9": "\u20a9",       # â© -> ₩
    "\u00c2\u00b0": "\u00b0",       # ° -> °
    "\u00c2\u00aa": "\u00aa",       # ª -> ª
    "\u00c2\u00ba": "\u00ba",       # º -> º
    "\u00c2\u00b2": "\u00b2",       # ² -> ²
    "\u00c2\u00b3": "\u00b3",       # ³ -> ³
    "\u00c2\u00bd": "\u00bd",       # ½ -> ½
    "\u00c2\u00bc": "\u00bc",       # ¼ -> ¼
    "\u00c2\u00be": "\u00be",       # ¾ -> ¾
    "\u00c2\u00a3": "\u00a3",       # £ -> £
    "\u00c2\u00a5": "\u00a5",       # ¥ -> ¥
    "\u00c2\u00a7": "\u00a7",       # § -> §
    "\u00c2\u00ab": "\u00ab",       # « -> «
    "\u00c2\u00bb": "\u00bb",       # » -> »
    "\u00c2\u00b7": "\u00b7",       # · -> ·
    "\u00e2\u20a2": "\u20a2",       # â¢ -> ¢ (alt)
    "\u00e2\u201a\u00ac": "\u20ac",  # € -> €
    # double-encoded accent patterns (√° style)
    "\u00e2\u0088\u009a\u00c2\u00b0": "\u00e1",
    "\u00e2\u0088\u009a\u00c2\u00a2": "\u00e2",
    "\u00e2\u0088\u009a\u00c2\u00a9": "\u00e9",
    "\u00e2\u0088\u009a\u00c2\u00b9": "\u00ed",
    "\u00e2\u0088\u009a\u00c2\u00ba": "\u00fa",
    "\u00e2\u0088\u009a\u00c2\u00b3": "\u00f3",
    "\u00e2\u0088\u009a\u00c2\u00a3": "\u00e3",
    "\u00e2\u0088\u009a\u00c3\u0087": "\u00e7",
    "\u00e2\u0088\u009a\u00c3\u0089": "\u00c9",
    "\u00e2\u0088\u009a\u00c3\u0093": "\u00d3",
    "\u00e2\u0088\u009a\u00c3\u009c": "\u00dc",
    "\u00e2\u0088\u009a\u00c3\u00b1": "\u00f1",
    "\u00e2\u0088\u009a\u00c2\u00a7": "\u00a7",
    "\u00e2\u0088\u009a\u00c3\u00a7": "\u00e7",
    # variants where the stray Â is missing but bytes are the same pattern
    "\u00e2\u0088\u009a\u00b0": "\u00e1",
    "\u00e2\u0088\u009a\u00a2": "\u00e2",
    "\u00e2\u0088\u009a\u00a9": "\u00e9",
    "\u00e2\u0088\u009a\u00b9": "\u00ed",
    "\u00e2\u0088\u009a\u00ba": "\u00fa",
    "\u00e2\u0088\u009a\u00b3": "\u00f3",
    "\u00e2\u0088\u009a\u00a3": "\u00e3",
    "\u00e2\u0088\u009a\u00c7": "\u00e7",
    "\u00e2\u0088\u009a\u00c9": "\u00c9",
    "\u00e2\u0088\u009a\u00d3": "\u00d3",
    "\u00e2\u0088\u009a\u00dc": "\u00dc",
    "\u00e2\u0088\u009a\u00f1": "\u00f1",
    "\u00e2\u0088\u009a\u00a7": "\u00a7",
    "\u00e2\u0088\u009a\u00e7": "\u00e7",
    # variants without the stray Â
    "\u221a\u00b0": "\u00e1",
    "\u221a\u00a2": "\u00e2",
    "\u221a\u00a9": "\u00e9",
    "\u221a\u00b9": "\u00ed",
    "\u221a\u00ba": "\u00fa",
    "\u221a\u00b3": "\u00f3",
    "\u221a\u00a3": "\u00e3",
    "\u221a\u00c7": "\u00e7",
    "\u221a\u00c9": "\u00c9",
    "\u221a\u00d3": "\u00d3",
    "\u221a\u00dc": "\u00dc",
    "\u221a\u00f1": "\u00f1",
    "\u221a\u00a7": "\u00a7",
    "\u221a\u00e7": "\u00e7",
    # common emoji/check/arrow fragments
    "\u00e2\u009c\u0094": "✔",
    "\u00e2\u009c\u0093": "✓",
    "\u00e2\u009c\u0085": "✅",
    "\u00e2\u009c\u00a8": "✨",
    "\u00e2\u009d\u0097": "‼",
    "\u00e2\u009d\u0095": "❕",
    "\u00e2\u009d\u0093": "❓",
    "\u00e2\u009c\u00b6": "✶",
    "\u00e2\u009e\u0098": "✘",
    "\u00e2\u0086\u0092": "→",
    "\u00e2\u0086\u0093": "↓",
    "\u00e2\u0086\u0091": "↑",
    "\u00e2\u0086\u0090": "←",
    "\u00e2\u0086\u009b": "↛",
    "\u00e2\u0086\u009c": "↜",
    "\u00e2\u0086\u009d": "↝",
    "\u00e2\u00ac\u0085": "⬅",
    "\u00e2\u00ac\u0086": "⬆",
    "\u00e2\u00ac\u0087": "⬇",
    "\u00e2\u0098\u00ba": "☺",
    "\u00f0\u009f\u0092\u00a1": "💡",
    "\u00f0\u009f\u0092\u00af": "💯",
    "\u00f0\u009f\u0093\u0097": "📗",
    "\u00f0\u009f\u0093\u009a": "📚",
    "\u00f0\u009f\u0093\u009d": "📝",
    "\u00f0\u009f\u0092\u00b8": "💸",
    "\u00f0\u009f\u0091\u008d": "👍",
    "\u00f0\u009f\u0091\u008e": "👎",
    "\u00f0\u009f\u0091\u008f": "👏",
    "\u00f0\u009f\u0098\u008a": "😊",
    "\u00f0\u009f\u008e\u0089": "🎉",
    "\u00f0\u009f\u0093\u00a2": "📢",
    "\u00f0\u009f\u0094\u0096": "🔖",
    "\u00f0\u009f\u0094\u00a9": "🔩",
    "\u00f0\u009f\u0094\u00b9": "🔹",
}

# Tokens for quick detection; include map keys plus a few extras
MOJIBAKE_TOKENS: tuple[str, ...] = tuple(
    set(
        list(MOJIBAKE_MAP.keys())
        + [
            "\u00c3\u00a0",
            "\u00c3\u00a2",
            "\u00c3\u00a3",
            "\u00c3\u00a7",
            "\u00c3\u00a9",
            "\u00c3\u00aa",
            "\u00c3\u00b5",
            "\u00e2\u20ac\u201d",
            "\u00e2\u20ac\u201c",
        ]
    )
)

ALLOWED_SUFFIXES: set[str] = {
    ".py",
    ".json",
    ".csv",
    ".md",
    ".txt",
    ".yml",
    ".yaml",
    ".ini",
    ".toml",
}

SKIP_DIRS: set[str] = {".git", ".ruff_cache", "__pycache__", ".vscode", ".qodo"}


def has_mojibake(text: str) -> bool:
    return any(tok in text for tok in MOJIBAKE_TOKENS)


def apply_fixes(text: str) -> str:
    fixed = text
    for bad, good in MOJIBAKE_MAP.items():
        if bad in fixed:
            fixed = fixed.replace(bad, good)
    return fixed


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_dir():
            if path.name in SKIP_DIRS:
                continue
            continue
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            continue
        yield path


def process_file(path: Path) -> bool:
    try:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="latin-1")
    except Exception as exc:
        print(f"[ERRO] Falha ao ler {path}: {exc}")
        return False

    if not has_mojibake(text):
        return False

    fixed = apply_fixes(text)
    if fixed == text:
        return False

    try:
        path.write_text(fixed, encoding="utf-8")
        print(f"[OK] Corrigido: {path}")
        return True
    except Exception as exc:
        print(f"[ERRO] Falha ao escrever {path}: {exc}")
        return False


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
    if not root.exists():
        print(f"Caminho inexistente: {root}")
        return 1

    total = 0
    changed = 0
    for file_path in iter_files(root):
        total += 1
        if process_file(file_path):
            changed += 1

    print(f"\nArquivos analisados: {total}")
    print(f"Arquivos corrigidos: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
