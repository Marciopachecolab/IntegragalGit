# -*- coding: utf-8 -*-
import pathlib
mapping={
    "\u00c3\u00a1": "á",
    "\u00c3\u00a9": "é",
    "\u00c3\u00aa": "ê",
    "\u00c3\u00ad": "í",
    "\u00c3\u00b3": "ó",
    "\u00c3\u00b4": "ô",
    "\u00c3\u00ba": "ú",
    "\u00c3\u00a3": "ã",
    "\u00c3\u00b5": "õ",
    "\u00c3\u00a7": "ç",
    "\u00c3\u00a0": "à",
    "\u00c3\u0081": "Á",
    "\u00c3\u0089": "É",
    "\u00c3\u009a": "Ú",
    "\u00c3\u008a": "Ê",
    "\u00c3\u0093": "Ó",
    "\u00c3\u0083": "Ã",
    "\u00c3\u0087": "Ç",
    "\u00c3\u00a2": "â",
    "\u00c3\u0082": "Â",
    "\u00c3\u00b1": "ñ",
}
root=pathlib.Path('.')
fixed=0
for p in root.rglob('*'):
    if not p.is_file():
        continue
    if p.name in {"test_mojibake_scan.py","fix_mojibake_project.py","tmp_fix.py"}:
        continue
    try:
        text=p.read_text(encoding='utf-8')
    except Exception:
        continue
    if "Ã" not in text:
        continue
    new=text
    for k,v in mapping.items():
        new=new.replace(k,v)
    if new!=text:
        p.write_text(new,encoding='utf-8')
        fixed+=1
        print('fixed',p)
print('done fixed',fixed)
