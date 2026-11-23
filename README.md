# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/Daniikhwan/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/Daniikhwan/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

One image summing up the world news of Monday 23 November 2026.

`main.py` (Python 3.13, standard library only, no network) draws the
front page from scratch — a small rasteriser with a hand-built 5x7
bitmap font — and writes it to `$MAKEFUN_OUTPUT_DIR/entry.png`
(default `/output/entry.png`). The output is deterministic: two runs
write byte-identical PNG files.

## The six stories

1. **Hormuz attacks at highest level since war began** — three tankers
   struck since Friday as Tehran presses its grip on the vital
   waterway; Trump favours an economic squeeze over new strikes; the
   US blockade enters day 130 (CNN).
2. **14 missing after drone hits flats near Kyiv** — a Russian drone
   collapses part of a five-storey block in Dymer; one dead, nine
   rescued (Reuters).
3. **COP31 ends with no deal on fossil fuels** — talks in Antalya
   collapse after the final draft dropped any mention of fossil
   fuels; the EU said no (AFP).
4. **50 missing after candy factory fire** — a blaze rips through a
   three-storey plant in Banten, Indonesia; seven body bags recovered
   (Reuters).
5. **Thousands march in Lisbon over living costs** — crowds fill the
   streets as anger over prices and rents boils over.
6. **24 civilians killed in fresh South Sudan violence** — fighting
   flares again as the UN warns of a deepening crisis (AFP).

Also today: Nepal's PM in Delhi for talks with Modi; South Korea's
education minister quits over an AI exam-cheating scandal; the UN
agrees to keep negotiating on lethal AI weapons; Kim Jong Un says
North Korea seeks security, not supremacy.

## Run it

```sh
python3 main.py
```
