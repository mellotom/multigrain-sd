# builds data.json for the multigrain-sd page from build/inventory.json
# inventory.json comes from build/inventory.py run against the card (see README)
# usage: python3 build/build.py
import json, os, re, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
inv = json.load(open(os.path.join(HERE, 'inventory.json'), encoding='utf-8'))

CATS = ['key', 'pad', 'sng', 'stk', 'tex', 'vox']
BANKS = ['x', 'y', 'z', 'xx', 'yy', 'zz']
NOTE = r'[A-G](?:#|b)?'

def key_of(stem):
    """key as written in the file name, or '' when the name doesn't state one"""
    toks = stem.split('_')
    for t in reversed(toks[2:]):
        m = re.fullmatch(rf'({NOTE})(m|min|minor|maj|major|maj7)?', t)
        if m:
            q = m.group(2) or ''
            q = 'm' if q in ('m', 'min', 'minor') else ('maj7' if q == 'maj7' else ('' if q == '' else ''))
            return m.group(1) + q
        m = re.fullmatch(rf'({NOTE})(min|maj)(?:or)?', t)
        if m:
            return m.group(1) + ('m' if m.group(2) == 'min' else '')
    return ''

def bpm_of(stem):
    toks = stem.split('_')[2:]
    for t in toks:
        m = re.fullmatch(r'(?:bpm)?(\d{2,3})(?:bpm)?', t, flags=re.I)
        if m and 60 <= int(m.group(1)) <= 180:
            return int(m.group(1))
    return 0

LABELS = json.load(open(os.path.join(HERE, 'labels.json'), encoding='utf-8')) if os.path.exists(os.path.join(HERE, 'labels.json')) else {}
projects = []
for p, name in sorted(inv['projects'].items()):
    n = int(p[-2:])
    rows = [r for r in inv['rows'] if r['project'] == p]
    label = name.split('_', 1)[1] if '_' in name else name
    label = LABELS.get(p, label.replace('_', ' '))
    projects.append(dict(p=p, n=n, name=label, bank=BANKS[(n - 1) // 8], btn=(n - 1) % 8 + 1,
                         files=len(rows), sec=round(sum(r['sec'] for r in rows), 1)))
packs = sorted({r['pack'] for r in inv['rows'] if r['pack']}, key=str.lower)
rows = []
for r in inv['rows']:
    stem = r['file'][:-4]
    rows.append([int(r['project'][-2:]), r['pos'], CATS.index(r['cat']) if r['cat'] in CATS else -1,
                 r['file'], packs.index(r['pack']) if r['pack'] else -1, key_of(stem), bpm_of(stem), r['sec']])
out = dict(v=datetime.date.today().strftime('%Y.%m.%d'), cats=CATS, projects=projects, packs=packs,
           cols=['project', 'pos', 'cat', 'file', 'pack', 'key', 'bpm', 'sec'], rows=rows,
           empty=inv.get('empty', []))
json.dump(out, open(os.path.join(HERE, '..', 'data.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
page = open(os.path.join(HERE, 'page.html'), encoding='utf-8').read().replace('/*CSS*/', open(os.path.join(HERE, 'base.css'), encoding='utf-8').read())
open(os.path.join(HERE, '..', 'index.html'), 'w', encoding='utf-8').write(page)
print(len(projects), 'projects', len(rows), 'files', len(packs), 'packs')
