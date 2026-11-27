# One Day on Earth — Friday 27 November 2026

[![Bounty](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127)
[![Rank](https://make.fun/badge/news-image-20261127/renprayoga/news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127)
[![Reward](https://make.fun/badge/news-image-20261127/renprayoga/news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127)

One image that sums up the world's news of **Friday 27 November 2026**,
drawn as a newspaper front page: a bold masthead with the date checked, one
dominant lead with a drawn night scene over the Gulf, two illustrated
stories, a west-to-east strip of the eleven places where the day happened,
a Trade & Markets band with mini charts, and a two-column Day in Brief.

## The day in the picture

- **Lead — Iranian drone strike kills two Italians in Kuwait:** two Italian
  technicians working for German defence group Rheinmetall are killed in a
  drone attack Kuwait blames on Iran; Tehran denies any role, and Rome
  demands answers as Gulf tensions climb.
- **Hamas weighs reply after Israel kills 10 in Gaza:** Israel kills 10
  people in Gaza and Hamas weighs its response, putting the fragile
  ceasefire under fresh strain.
- **Russia hits two grain ships off Odesa:** Moscow strikes two foreign
  cargo ships carrying more than 100,000 tonnes of grain near Ukraine's
  Black Sea ports.
- **Trade & Markets:** US shoppers spend on despite inflation, with holiday
  sales seen past $1 trillion; Tokyo core inflation tops the Bank of Japan's
  2% target for a third month at +2.9%; Trump seeks a probe into "fake" GDP
  figures as growth is revised up to 4.3%.
- **Also today:** UK net migration falls to its lowest since 1997; Gérard
  Depardieu is to stand trial over a 2018 rape claim; a tanker capsizes off
  Ibiza, killing one; Elon Musk says every US child will get two SpaceX
  shares; Gukesh and Sindarov draw a marathon Game 3 of the World Chess
  Championship; New Zealand reach 77-1 at lunch in the 2nd Test v India; a
  storm halts the 100th Macy's Thanksgiving Day Parade and leaves 500,000
  homes dark; Ebola in Congo passes 12,000 cases; Kim Jong Un vows permanent
  nuclear armament; Guinea-Bissau delays its polls two years after the coup;
  Serbia sets its presidential vote for 27 December; Brazil inflation eases;
  Indian rupee bulls return after 18 months; Argentina's Senate suspends the
  2027 primaries; Nyrstar halts Dutch zinc output; China's drones reshape
  Asian militaries; New Zealand's final election count is due.

Sources: Reuters, BBC, CNN, AFP, AP.

## How it runs

`main.py` (Python 3.13, standard library only) draws the page procedurally
with `render.py` — a tiny deterministic raster engine with a hand-built 5x7
pixel font and a hand-written PNG encoder — and writes `entry.png`
(1024x1024, well under 1 MiB) to `$MAKEFUN_OUTPUT_DIR` (default `/output`).
No network, no fonts from disk, no timestamps in the output: two runs write
byte-identical files.

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see `LICENSE`.
