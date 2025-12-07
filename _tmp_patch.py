# -*- coding: latin-1 -*-
from pathlib import Path
p=Path('services/plate_viewer.py')
text=p.read_text(encoding='latin-1')
text=text.replace('.strip().replace(" ", "").replace(" ", "")','.strip().replace(" ", "")')
p.write_text(text,encoding='latin-1')
