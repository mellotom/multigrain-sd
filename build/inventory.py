# run on the computer with the multigrain card mounted:
#   python3 build/inventory.py "/Volumes/NO NAME/Multigrain" "<splice packs folder>" build/inventory.json
# lists every project folder and .wav on the card (alphabetical = the order the module steps through),
# checks the format (48 khz · 16-bit · stereo · <= 32 s) with ffprobe, and finds each file's source pack
import os, re, sys, json, subprocess
sd, packdir, out = sys.argv[1:4]
packs = {}
for root, _, files in os.walk(packdir):
    for f in files:
        if f.startswith('._') or not f.lower().endswith(('.wav', '.aif', '.aiff')): continue
        packs.setdefault(os.path.splitext(f)[0].lower(), os.path.relpath(root, packdir).split(os.sep)[0])
keys = list(packs)
idx = {}
p = os.path.join(sd, '_index.txt')
if os.path.exists(p):
    for l in open(p, encoding='utf-8'):
        if '=' in l: a, b = l.split('=', 1); idx[a.strip()] = b.strip()
def probe(f):
    j = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=sample_rate,channels,bits_per_sample:format=duration', '-of', 'json', f], capture_output=True, text=True).stdout)
    st = j['streams'][0]
    return dict(sr=int(st['sample_rate']), ch=st['channels'], bits=st.get('bits_per_sample'), sec=round(float(j['format']['duration']), 2))
rows, empty = [], []
for proj in sorted(d for d in os.listdir(sd) if re.fullmatch(r'Project\d\d', d)):
    files = sorted(f for f in os.listdir(os.path.join(sd, proj)) if f.lower().endswith('.wav') and not f.startswith('._'))
    if not files: empty.append(proj); continue
    for i, f in enumerate(files):
        m = re.match(r'([a-z]+)_(\d+)_(.*)', f[:-4])
        cat, slot, orig = (m.group(1), int(m.group(2)), m.group(3)) if m else ('', 0, f[:-4])
        pk = packs.get(orig.lower())
        if not pk:
            c = [k for k in keys if k.startswith(orig.lower())]
            pk = packs[c[0]] if len(c) == 1 else ''
        rows.append(dict(project=proj, name=idx.get(proj, ''), pos=i + 1, cat=cat, slot=slot, file=f, pack=pk, **probe(os.path.join(sd, proj, f))))
bad = [r['file'] for r in rows if r['sr'] != 48000 or r['bits'] != 16 or r['ch'] != 2 or r['sec'] > 32]
json.dump(dict(projects={k: v for k, v in sorted(idx.items()) if any(r['project'] == k for r in rows)}, rows=rows, empty=empty), open(out, 'w', encoding='utf-8'), indent=0, ensure_ascii=False)
print(len(rows), 'files', len(empty), 'empty folders', 'BAD FORMAT: ' + ', '.join(bad) if bad else 'all files load')
