#!/usr/bin/env python

"""Debug: Verificar porque registry não carrega novo exame"""




from services.exam_registry import registry



# Recarregar registry

print("Antes de recarregar:")

print(f"Total de exames: {len(registry.exams)}")

print(f"Slugs: {list(registry.exams.keys())}")



# Carregar novamente

print("\nRecarregando registry...")

registry.load()



print("\nDepois de recarregar:")

print(f"Total de exames: {len(registry.exams)}")

print(f"Slugs: {list(registry.exams.keys())}")



# Verificar se arquivo JSON existe

import json

from pathlib import Path



json_file = Path("config/exams/teste_covid19.json")

print(f"\nArquivo {json_file} existe? {json_file.exists()}")



if json_file.exists():

    with open(json_file) as f:

        data = json.load(f)

    print(f"Nome no JSON: {data.get('nome_exame')}")

    print(f"Slug no JSON: {data.get('slug')}")

