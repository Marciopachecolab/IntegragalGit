# tests/test_mojibake_scan.py
#
# Objetivo:
# - Percorrer TODO o projeto (pastas e subpastas),
# - Ler arquivos de texto em UTF-8,
# - Verificar se existe ALGUMA das sequências típicas de mojibake
#   (Ã, âœ, âž, ðŸ etc.),
# - Permitir acentos normais em UTF-8 (á, é, í, ó, ú, ç, ã, õ, etc.).
#
# Se encontrar alguma sequência de mojibake, o teste FALHA e mostra
# quais arquivos e quais sequências foram encontradas.
#
# Observação: este próprio arquivo de teste e o script de correção
# fix_mojibake_project.py contêm essas sequências de propósito,
# por isso são explicitamente ignorados.

from pathlib import Path

# Extensões tratadas como arquivos de texto do projeto
TEXT_EXTENSIONS = {
    ".py",
    ".txt",
    ".md",
    ".rst",
    ".csv",
    ".tsv",
    ".ini",
    ".cfg",
    ".json",
    ".yml",
    ".yaml",
}

# Diretórios a ignorar
EXCLUDED_DIR_NAMES = {
    ".git",
    ".idea",
    ".vscode",
    ".pytest_cache",
    "__pycache__",
    "venv",
    ".venv",
}

# Arquivos específicos a ignorar (pois contêm as sequências como *padrão* de busca)
EXCLUDED_FILE_NAMES = {
    "test_mojibake_scan.py",   # este próprio teste
    "fix_mojibake_project.py", # script de correção com as sequências na lista
}

# Sequências TÍPICAS de mojibake geradas por UTF-8 lido como Latin-1/1252,
# incluindo prefixos de emojis quebrados.
MOJIBAKE_SEQUENCES = [
    # Acentos quebrados em português
    "á",
    "é",
    "ê",
    "è",
    "í",
    "ó",
    "ô",
    "ò",
    "ú",
    "ã",
    "õ",
    "ç",
    "Á",
    "É",
    "Ê",
    "Ãˆ",
    "Ó",
    "Ô",
    "Ã’",
    "Ú",
    "Ã",
    "Õ",
    "Ç",

    # Aspas, traços e símbolos tipográficos quebrados
    "–",  # en dash / hífen
    "—",  # em dash
    "\u201c",  # aspas de abertura
    "\u201d",  # aspas de fechamento (forma comum)
    "\u2018",  # aspas simples de abertura
    "\u2019",  # aspas simples de fechamento
    "•",  # bullet
    "…",  # reticências

    # Prefixos genéricos de emojis quebrados
    "âœ",   # pedaço de check / símbolo
    "âž",   # pedaço de seta, botão, etc.
    "ðŸ",   # prefixo de praticamente todos emojis quebrados
]


def is_text_file(path: Path) -> bool:
    """Define se o arquivo deve ser inspecionado como texto."""
    return path.suffix.lower() in TEXT_EXTENSIONS


def should_skip_dir(path: Path) -> bool:
    """Define se um diretório deve ser ignorado (venv, cache, etc.)."""
    return path.name in EXCLUDED_DIR_NAMES


def should_skip_file(path: Path) -> bool:
    """Define se um arquivo específico deve ser ignorado."""
    return path.name in EXCLUDED_FILE_NAMES


def test_no_mojibake_sequences():
    """
    Garante que não existam sequências típicas de mojibake no código-fonte.
    Acentos NORMAIS em UTF-8 (á, é, í, ó, ú, ç, ã, õ etc.) são PERMITIDOS.

    O teste só falha se encontrar as sequências declaradas em MOJIBAKE_SEQUENCES
    em arquivos que não estejam na lista de exclusão.
    """
    # Raiz do projeto = pasta acima de tests/
    project_root = Path(__file__).resolve().parents[1]

    problemas = []  # lista de tuplas (arquivo, sequencia, contexto)

    for path in project_root.rglob("*"):
        if path.is_dir():
            if should_skip_dir(path):
                # pula diretórios como venv, caches, etc.
                continue
            else:
                continue

        if not path.is_file():
            continue

        if should_skip_file(path):
            # ignora este próprio teste e o script de correção
            continue

        if not is_text_file(path):
            continue

        try:
            # Leitura em UTF-8; se algo estiver REALMENTE corrompido,
            # usamos errors="replace" para não quebrar o teste.
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            # Se não conseguiu ler, registrar como aviso de inspeção,
            # mas não necessariamente falhar por mojibake.
            problemas.append((str(path), f"<ERRO DE LEITURA: {e}>", ""))
            continue

        for seq in MOJIBAKE_SEQUENCES:
            idx = content.find(seq)
            if idx != -1:
                left = max(0, idx - 40)
                right = min(len(content), idx + len(seq) + 40)
                snippet = content[left:right].replace("\n", "\\n")
                problemas.append((str(path), seq, snippet))

    if problemas:
        msg_lines = ["Foram encontradas sequências típicas de MOJIBAKE no projeto:"]
        for arquivo, seq, ctx in problemas:
            msg_lines.append(f"- Arquivo: {arquivo}")
            msg_lines.append(f"  Sequência: {repr(seq)}")
            if ctx:
                msg_lines.append(f"  Contexto: {ctx}")
            msg_lines.append("")
        full_msg = "\n".join(msg_lines)
        assert False, full_msg
    else:
        # Mensagem explícita para o seu caso de sucesso
        print(
            "0 ocorrências de sequências típicas de mojibake "
            "(Ã, âœ, ðŸ etc.). Acentos normais em UTF-8 são permitidos."
        )
        assert True
