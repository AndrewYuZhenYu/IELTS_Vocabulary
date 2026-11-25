"""Read Oxford's downloadable PDFs locally for comparison; do not redistribute them."""
from pathlib import Path
import re
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'Data' / 'References'
PATTERN = re.compile(r'^(.+?)\s+(?:n\.|v\.|adj\.|adv\.|pron\.|prep\.|conj\.|det\.|auxiliary v\.|modal v\.|indefinite article|definite article|exclam\.|number|ordinal number|phrasal verb|abbr\.)')
LEVELS = {'A1','A2','B1','B2','C1'}

def extract_pdf(path):
    words = {}; phrases=[]; level=None
    reader=PdfReader(path)
    for page in reader.pages:
        for raw in page.extract_text().splitlines():
            line=raw.strip().replace('\xa0',' ')
            if line in LEVELS:
                level=line;continue
            match=PATTERN.match(line)
            if not match or not level:continue
            word=match.group(1).lower().strip()
            word=re.sub(r'\s*\([^)]*\)','',word)
            word=re.sub(r'\d+$','',word)
            if word=='a, an':
                words['a']=level;words['an']=level;continue
            if re.fullmatch(r'[a-z]+(?:-[a-z]+)?',word):
                if word not in words or ['A1','A2','B1','B2','C1'].index(level)<['A1','A2','B1','B2','C1'].index(words[word]):words[word]=level
            else:phrases.append(word)
    return words,phrases

def load_oxford():
    paths=[REF/'oxford3000.pdf',REF/'oxford5000.pdf']
    if not all(p.exists() for p in paths):
        raise FileNotFoundError('Oxford reference PDFs missing; run download_sources.py first')
    ox3000,phrases3000=extract_pdf(paths[0])
    ox5000,phrases5000=extract_pdf(paths[1])
    if not (2900<=len(ox3000)<=3100 and 1900<=len(ox5000)<=2100):
        raise ValueError(f'Unexpected Oxford extraction counts: {len(ox3000)}, {len(ox5000)}')
    merged={w:(level,'Oxford 3000') for w,level in ox3000.items()}
    for w,level in ox5000.items():merged.setdefault(w,(level,'Oxford 5000 extension'))
    return ox3000,ox5000,merged,phrases3000+phrases5000
