# Chaos, Drawn

Chaos theory in plain words, with every picture drawn from the equation that makes it, the
mathematics printed and then read out loud, and the two tools for living with chaos worked through
in full: the law of large numbers, and resilient systems.

**Live:** https://nanobotco.github.io/chaos/

## What is on it

- **The one idea** — sensitive dependence on initial conditions, shown with two logistic runs a
  ten-thousandth apart, and the stretch-and-fold engine under every chaotic map.
- **One rule into chaos** — the logistic map, cobweb by cobweb; the bifurcation tree; period
  doubling; Feigenbaum's constant found in the spacing of the forks; the period-three window and
  Li–Yorke.
- **Weather & the butterfly** — the Lorenz system stepped with Runge–Kutta 4; the forecast horizon;
  the Lyapunov exponent measured by Benettin's method.
- **The law of large numbers** — the running average of a die closing on 3.5, and the long-run shape
  of a fully chaotic map turning out to be an exact curve. Chaos in the one, law in the many.
- **Resilient systems** — four drawn moves: negative feedback, redundancy (and the shared-cause trap),
  diversification, and margin to the tipping point.
- **The code** — the whole mathematics in one dependency-free Python file that runs in under a second.
- **Words** (19 terms) · **Sources** (24).

## Every figure is computed, not drawn by hand

`tools/figures.py` computes all fourteen figures from the equations and emits them as inline SVG.
Nothing on the site is a stock image. The numbers the copy quotes are read from `build/facts.json`,
so the words can never drift from the arithmetic.

| figure | what the run found |
|---|---|
| logistic period doublings | r = 2.998, 3.449, 3.544, 3.564 |
| Feigenbaum ratio (last spacing on this run) | 4.64, closing on the known 4.669 |
| Lorenz largest Lyapunov exponent (Benettin) | 0.92, against the textbook 0.906 |
| average of 3,000 die rolls | 3.499 (true 3.5) |
| a shock, no feedback vs one feedback loop | drifts to 6.92, held to 0.61 |

Run it yourself:

```
python3 chaos.py          # the standalone: chaos, the two tools, and the proof, in one file
python3 tools/figures.py  # redraw every figure and print the numbers
```

## Build

```
python3 tools/figures.py                                    # draw the figures
SITE_URL=https://nanobotco.github.io/chaos python3 tools/site.py
./publish.sh                                                # gates on style + host paths, writes docs/
python3 tools/serve.py 8854                                 # preview at http://127.0.0.1:8854/chaos/
```

GitHub Pages serves `docs/` from `main`.

## Licence

Text and figures: [CC BY 4.0](LICENSE). The code that draws them: [MIT](LICENSE-CODE). Keep the
credit line and you may use any of it.
