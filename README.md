# multigrain-sd

travelers guide for navigating the grain archive: a live, searchable list of every project folder and sample on my intellijel multigrain microsd card. hidden entry point: the sd card slot on the multigrain guide's front panel.

live page: https://mellotom.github.io/multigrain-sd/

- one folder per project (`/Multigrain/Project01`–`48`); `_index.txt` on the card names each one
- every file is .wav, 48 khz, 16-bit, stereo, 32 s or less (the only format the module loads)
- file names carry a category prefix + number so each family stays together when stepping through /project:
  `key` keys · `pad` pads · `sng` songstarters · `stk` melodic stacks · `tex` textures · `vox` vocals
- key and bpm columns are read from the file names; blank when the name doesn't say

## updating

1. `python3 build/inventory.py "/Volumes/NO NAME/Multigrain" "<splice packs folder>" build/inventory.json`
2. edit `build/labels.json` for any project display names
3. `python3 build/build.py` → writes `data.json` and `index.html`

reference: multigrain manual 1.4 (sample guide, projects, microsd card).

design homage to the house of x / powers of x data pages by tom muller with jonathan hickman. not affiliated with intellijel, splice or marvel. samples are not included in this repo.
