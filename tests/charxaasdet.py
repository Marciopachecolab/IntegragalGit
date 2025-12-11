#!/usr/bin/env python

"""

Scanner de codificação e gerador de relatório de análise.



- Percorre recursivamente um diretório base.

- Detecta a provável codificação de cada arquivo usando chardet.

- Classifica arquivos possivelmente binários.

- Gera um arquivo de relatório relatorio_analise.txt no diretório base,

  descrevendo cada diretório e subdiretório encontrado.

"""



import os

from pathlib import Path

from dataclasses import dataclass

from typing import Dict, List, Optional



import chardet





@dataclass

class FileEncodingInfo:

    path: Path

    encoding: Optional[str]

    confidence: float

    is_binary: bool





def detect_encoding(file_path: Path, sample_size: int = 1024 * 1024) -> FileEncodingInfo:

    """

    Detecta a codificação de um arquivo usando chardet.



    Se o arquivo parecer binário ou a confiança for muito baixa,

    marca como binário.

    """

    try:

        with file_path.open("rb") as f:

            raw = f.read(sample_size)

    except Exception:

        # Não foi possível ler o arquivo – trata como binário/desconhecido

        return FileEncodingInfo(path=file_path, encoding=None, confidence=0.0, is_binary=True)



    if not raw:

        # Arquivo vazio – considera como texto ASCII "trivial"

        return FileEncodingInfo(path=file_path, encoding="ascii", confidence=1.0, is_binary=False)



    detection = chardet.detect(raw)

    encoding = detection.get("encoding")

    confidence = float(detection.get("confidence") or 0.0)



    # Heurística simples para binário:

    # - se encoding é None

    # - ou se confiança muito baixa

    # - ou se há muitos bytes nulos

    null_bytes_ratio = raw.count(b"\x00") / len(raw)

    is_probably_binary = (

        encoding is None

        or confidence < 0.25

        or null_bytes_ratio > 0.05

    )



    return FileEncodingInfo(

        path=file_path,

        encoding=encoding,

        confidence=confidence,

        is_binary=is_probably_binary,

    )





def scan_directory(base_dir: Path) -> Dict[Path, List[FileEncodingInfo]]:

    """

    Percorre recursivamente base_dir e retorna um dicionário:

        { caminho_do_diretorio: [FileEncodingInfo, ...] }

    """

    results: Dict[Path, List[FileEncodingInfo]] = {}



    for root, dirs, files in os.walk(base_dir):

        dir_path = Path(root)

        dir_results: List[FileEncodingInfo] = []



        for filename in files:

            file_path = dir_path / filename



            # Ignora alguns tipos claramente binários a priori (opcional)

            if file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".xlsx", ".xls"}:

                info = FileEncodingInfo(

                    path=file_path,

                    encoding=None,

                    confidence=0.0,

                    is_binary=True,

                )

            else:

                info = detect_encoding(file_path)



            dir_results.append(info)



        results[dir_path] = dir_results



    return results





def summarize_encodings(file_infos: List[FileEncodingInfo]) -> Dict[str, int]:

    """

    Gera um resumo simples: { "encoding_ou_tipo": contagem }

    """

    summary: Dict[str, int] = {}

    for info in file_infos:

        if info.is_binary:

            key = "binário/desconhecido"

        else:

            key = info.encoding or "desconhecido"



        summary[key] = summary.get(key, 0) + 1

    return summary





def write_report(base_dir: Path, results: Dict[Path, List[FileEncodingInfo]]) -> Path:

    """

    Escreve o arquivo relatorio_analise.txt no diretório base,

    descrevendo cada diretório e subdiretório.

    """

    report_path = base_dir / "relatorio_analise.txt"



    # Ordena diretórios em ordem alfabética

    sorted_dirs = sorted(results.keys(), key=lambda p: str(p))



    with report_path.open("w", encoding="utf-8") as f:

        f.write("RELATÓRIO DE ANÁLISE DE CODIFICAÇÃO\n")

        f.write(f"Diretório base: {base_dir}\n")

        f.write("=" * 80 + "\n\n")



        for dir_path in sorted_dirs:

            file_infos = results[dir_path]

            rel_dir = dir_path.relative_to(base_dir) if dir_path != base_dir else Path(".")



            f.write(f"DIRETÓRIO: {rel_dir}\n")

            f.write("-" * 80 + "\n")



            if not file_infos:

                f.write("  (nenhum arquivo neste diretório)\n\n")

                continue



            # Resumo por codificação / tipo

            summary = summarize_encodings(file_infos)

            total_files = len(file_infos)



            f.write(f"  Total de arquivos: {total_files}\n")

            f.write("  Resumo por codificação/tipo:\n")

            for enc, count in sorted(summary.items(), key=lambda x: x[0]):

                f.write(f"    - {enc}: {count} arquivo(s)\n")



            # Destaque de arquivos potencialmente problemáticos

            suspicious: List[FileEncodingInfo] = []

            for info in file_infos:

                if info.is_binary:

                    # Arquivo binário não é necessariamente problema – só marca se tiver extensão "de texto"

                    if info.path.suffix.lower() in {".py", ".txt", ".md", ".csv", ".sql", ".ini", ".cfg"}:

                        suspicious.append(info)

                else:

                    # Codificações "suspeitas" usadas em textos

                    if info.encoding in {"MacRoman", "Windows-1254", "Windows-1252"}:

                        suspicious.append(info)

                    elif info.confidence < 0.7:

                        suspicious.append(info)



            if suspicious:

                f.write("\n  Arquivos potencialmente problemáticos (mojibake / codificação incomum):\n")

                for info in suspicious:

                    rel_file = info.path.relative_to(base_dir)

                    enc = info.encoding or "desconhecida"

                    f.write(

                        f"    - {rel_file} -> {enc} "

                        f"(confiança={info.confidence:.3f}, "

                        f"{'binário' if info.is_binary else 'texto'})\n"

                    )

            else:

                f.write("\n  Nenhum arquivo potencialmente problemático identificado neste diretório.\n")



            # Lista detalhada de arquivos (opcional, mas útil para auditoria)

            f.write("\n  Lista detalhada de arquivos:\n")

            for info in sorted(file_infos, key=lambda i: i.path.name.lower()):

                rel_file = info.path.relative_to(base_dir)

                enc = info.encoding or "desconhecida"

                tipo = "binário" if info.is_binary else "texto"

                f.write(

                    f"    - {rel_file.name}: {enc} "

                    f"(confiança={info.confidence:.3f}, {tipo})\n"

                )



            f.write("\n\n")



    return report_path





def main():

    import argparse



    parser = argparse.ArgumentParser(

        description="Analisa codificações de arquivos e gera relatorio_analise.txt."

    )

    parser.add_argument(

        "base_dir",

        nargs="?",

        default=".",

        help="Diretório base para análise (padrão: diretório atual).",

    )



    args = parser.parse_args()

    base_dir = Path(args.base_dir).resolve()



    if not base_dir.exists() or not base_dir.is_dir():

        raise SystemExit(f"Diretório inválido: {base_dir}")



    print(f"Analisando diretório base: {base_dir}")

    results = scan_directory(base_dir)

    report_path = write_report(base_dir, results)

    print(f"Relatório gerado em: {report_path}")





if __name__ == "__main__":

    main()

