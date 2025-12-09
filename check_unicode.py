"""Check exact Unicode for Cт column."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.equipment_detector import analisar_estrutura_xlsx

arquivo = r"C:\Users\marci\Downloads\18 JULHO 2025\20250718 VR1-VR2 BIOM PLACA 5.xlsx"
est = analisar_estrutura_xlsx(arquivo)

print("\n" + "="*80)
print("ANÁLISE DE CARACTERES - Coluna 6")
print("="*80)

h6 = est['headers'][6]
h7 = est['headers'][7]

print(f"\nColuna 6: '{h6}'")
print(f"  Bytes (hex): {h6.encode('utf-8').hex()}")
print(f"  Caracteres:")
for c in h6:
    print(f"    '{c}' → U+{ord(c):04X} ({ord(c)}) → {c.encode('utf-8').hex()}")

print(f"\nColuna 7: '{h7}'")
print(f"  Bytes (hex): {h7.encode('utf-8').hex()}")
print(f"  Caracteres:")
for c in h7:
    print(f"    '{c}' → U+{ord(c):04X} ({ord(c)})")

print(f"\nComparação:")
print(f"  'Cт' contém 'cq'? {('cq' in h6.lower())}")
print(f"  'Cт' contém 'ct'? {('ct' in h6.lower())}")
print(f"  'Cт'.lower() = '{h6.lower()}'")
print(f"  Segundo char é т cirílico? {h6[1] == 'т'} (U+{ord(h6[1]):04X})")
print(f"  Segundo char é t latino? {h6[1] == 't'} (U+{ord('t'):04X})")

print("\n" + "="*80)
