"""
fix_mojibake_project.py

Script para varrer o projeto IntegraGAL, detectar sequências típicas de
mojibake (Ã¡, Ã£, â€“, â€” , â€œ, â€\x9d, âœ, âž, ðŸ etc.) e corrigi-las,
gravando os arquivos em UTF-8.

Regras principais:
- Apenas arquivos de TEXTO são processados (extensões conhecidas).
- Diretórios como venv, .git, caches, etc., são ignorados.
- Arquivos específicos (como este script e o teste de mojibake) são ignorados.
- As substituições são aplicadas em ordem decrescente de tamanho da chave,
  para evitar que sequências longas sejam divididas por substituições curtas.

Uso:
    python fix_mojibake_project.py
    python fix_mojibake_project.py --dry-run
    python fix_mojibake_project.py --root "C:/Users/marci/Downloads/Integragal"
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Tuple, List


# ---------------------------------------------------------------------------
# Configuração de diretórios / arquivos a ignorar
# ---------------------------------------------------------------------------

SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    ".idea",
    ".vscode",
    ".vs",
    ".tox",
    ".eggs",
    "dist",
    "build",
    "venv",
    ".venv",
}

# Arquivos que NÃO devem ser “corrigidos”
SKIP_FILE_NAMES = {
    "fix_mojibake_project.py",   # este próprio script
    "test_mojibake_scan.py",     # o teste que contém a lista de sequências
}

# Extensões de arquivos que consideramos texto
TEXT_EXTENSIONS = {
    ".py",
    ".txt",
    ".md",
    ".rst",
    ".csv",
    ".json",
    ".yml",
    ".yaml",
    ".ini",
    ".cfg",
    ".toml",
    ".sql",
    ".log",
    ".bat",
    ".ps1",
    ".sh",
}


def should_skip_dir(path: Path) -> bool:
    """Retorna True se o diretório deve ser ignorado."""
    return path.name in SKIP_DIR_NAMES


def should_skip_file(path: Path) -> bool:
    """Retorna True se o arquivo deve ser ignorado."""
    if path.name in SKIP_FILE_NAMES:
        return True
    # se tiver extensão que não consideramos texto, pula
    if path.suffix and path.suffix.lower() not in TEXT_EXTENSIONS:
        return True
    return False


def is_text_file(path: Path) -> bool:
    """
    Heurística simples: considera texto se a extensão estiver em TEXT_EXTENSIONS.
    (Evita abrir binários e arquivos grandes desnecessariamente.)
    """
    if not path.suffix:
        # Se quiser ser mais agressivo, poderíamos considerar alguns arquivos sem extensão,
        # mas, por segurança, aqui vamos pular.
        return False
    return path.suffix.lower() in TEXT_EXTENSIONS


# ---------------------------------------------------------------------------
# Mapeamento de sequências quebradas -> formas corretas em UTF-8
# ---------------------------------------------------------------------------

BROKEN_TO_FIXED: Dict[str, str] = {
    # ----------------------------------------------------------------------
    # 1. Acentos portugueses quebrados (resultado típico de UTF-8 lido como CP1252)
    # ----------------------------------------------------------------------
    "Ã¡": "á",
    "Ã©": "é",
    "Ãª": "ê",
    "Ã¨": "è",
    "Ã­": "í",
    "Ã³": "ó",
    "Ã´": "ô",
    "Ã²": "ò",
    "Ãº": "ú",
    "Ã£": "ã",
    "Ãµ": "õ",
    "Ã§": "ç",

    "Ã\x81": "Á",
    "Ã‰": "É",
    "ÃŠ": "Ê",
    "Ãˆ": "È",
    "Ã“": "Ó",
    "Ã”": "Ô",
    "Ã’": "Ò",
    "Ãš": "Ú",
    "Ãƒ": "Ã",  # A maiúsculo com til
    "Ã•": "Õ",
    "Ã‡": "Ç",

    # ----------------------------------------------------------------------
    # 2. Aspas tipográficas, bullets, reticências e traços quebrados
    #    (sequências típicas: â€œ, â€\x9d, â€˜, â€™, â€¢, â€¦, â€“, â€”)
    # ----------------------------------------------------------------------
    "â€“": "–",    # en dash / hífen
    "â€”": "—",    # em dash

    "â€œ": "“",    # aspas duplas de abertura
    "â€\x9d": "”",  # aspas duplas de fechamento
    "â€˜": "‘",    # aspas simples de abertura
    "â€™": "’",    # aspas simples de fechamento

    "â€¢": "•",    # bullet
    "â€¦": "…",    # reticências

    # ----------------------------------------------------------------------
    # 3. Emojis / símbolos com prefixos quebrados
    #    Aqui não é possível recuperar exatamente o emoji original sem os bytes
    #    originais em CP1252/UTF-8. Então fazemos um mapeamento "genérico",
    #    para pelo menos manter legível.
    # ----------------------------------------------------------------------

    # Checks / OK
    "âœ”ï¸": "✅",  # variante com seletor de variação (checkmark)
    "âœ”": "✅",    # check preenchido
    "âœ“": "✓",     # check simples

    # Prefixos residuais com "âœ" sem o resto da sequência:
    "âœï¸": "✅",   # tentativa de "check" com seletor mas truncado
    "âœ": "✓",      # qualquer sobra "âœ" vira check simples

    # Setas / símbolos de botão quebrados com prefixo "âž"
    "âž": "➜",      # seta genérica; se necessário, ajuste manual depois

    # Emojis em geral quebrados com prefixo "ðŸ"
    # Ex.: "ðŸš€", "ðŸ“‹", "ðŸ”§", "ðŸ”„" etc., viram "★"
    "ðŸ": "★",
}


# ---------------------------------------------------------------------------
# Função principal de correção
# ---------------------------------------------------------------------------

def fix_file(path: Path, dry_run: bool = False) -> Tuple[int, Dict[str, int]]:
    """
    Corrige um arquivo de texto, aplicando todas as substituições de BROKEN_TO_FIXED.

    Retorna:
        (total_substituicoes, dict_por_sequencia)
    """
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"[WARN] Erro ao ler {path}: {e}")
        return 0, {}

    original_content = content

    # Para evitar que chaves mais curtas quebrem chaves maiores,
    # ordenamos as sequências por tamanho decrescente.
    replacements_per_seq: Dict[str, int] = {}
    for broken in sorted(BROKEN_TO_FIXED.keys(), key=len, reverse=True):
        fixed = BROKEN_TO_FIXED[broken]
        count = content.count(broken)
        if count > 0:
            content = content.replace(broken, fixed)
            replacements_per_seq[broken] = count

    total_replacements = sum(replacements_per_seq.values())

    if total_replacements > 0 and not dry_run:
        try:
            path.write_text(content, encoding="utf-8", newline="")
        except Exception as e:
            print(f"[ERROR] Erro ao escrever {path}: {e}")
            return 0, {}

    # Se nada mudou, não conta como arquivo modificado
    if content == original_content:
        return 0, {}

    return total_replacements, replacements_per_seq


def run_fix(root: Path, dry_run: bool = False) -> None:
    """
    Varrre o projeto a partir de `root`, aplica correções e exibe um resumo.
    """
    print(f"==> Raiz do projeto para correção: {root}")
    print(f"==> Modo dry-run: {'SIM' if dry_run else 'NÃO'}")
    print("==> Iniciando varredura...\n")

    total_files_modified = 0
    total_global_replacements = 0
    global_seq_counts: Dict[str, int] = {}

    for path in root.rglob("*"):
        if path.is_dir():
            if should_skip_dir(path):
                # Não desce neste diretório
                # (rglob já cuida da descida; aqui só sinalizamos)
                continue
            else:
                continue

        if not path.is_file():
            continue

        if should_skip_file(path):
            continue

        if not is_text_file(path):
            continue

        rel_path = path.relative_to(root)
        replacements, seq_counts = fix_file(path, dry_run=dry_run)

        if replacements > 0:
            total_files_modified += 1
            total_global_replacements += replacements
            print(f"[OK] {rel_path} - {replacements} substituição(ões)")
            for seq, cnt in seq_counts.items():
                global_seq_counts[seq] = global_seq_counts.get(seq, 0) + cnt

    print("\n==> RESUMO FINAL")
    print(f"Arquivos modificados: {total_files_modified}")
    print(f"Total de substituições aplicadas: {total_global_replacements}")

    if global_seq_counts:
        print("\nDetalhamento por sequência (mojibake -> contagem):")
        # Ordena pela quantidade decrescente
        for seq, cnt in sorted(global_seq_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {repr(seq)} -> {cnt}")
    else:
        print("Nenhuma sequência de mojibake foi encontrada ou substituída.")

    if dry_run:
        print("\n[INFO] Modo dry-run: nenhum arquivo foi gravado.")
    else:
        print("\n[INFO] Correção concluída. Arquivos gravados em UTF-8.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Corrige sequências típicas de mojibake no projeto IntegraGAL e grava em UTF-8."
    )
    parser.add_argument(
        "--root",
        type=str,
        default=None,
        help="Caminho da raiz do projeto (padrão: pasta onde está este script).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas mostra o que seria alterado, sem gravar os arquivos.",
    )

    args = parser.parse_args()

    if args.root:
        root = Path(args.root).resolve()
    else:
        # Por padrão, considera a pasta onde está o script como raiz do projeto
        root = Path(__file__).resolve().parent

    run_fix(root, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
