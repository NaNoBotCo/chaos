#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""site.py — the pages, built from the computed figures in build/figs.json and the
numbers in build/facts.json.

    python3 tools/figures.py          # draw the pictures, find the numbers
    SITE_URL=https://nanobotco.github.io/chaos python3 tools/site.py
"""
from __future__ import annotations

import html
import json
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fleet  # noqa: E402
from css import CSS  # noqa: E402
import sources as S  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
SITE = BUILD / "site"
SITE_URL = os.environ.get("SITE_URL", "https://nanobotco.github.io/chaos").rstrip("/")
tail = SITE_URL.split("//", 1)[-1]
BASE = "/" + tail.split("/", 1)[1].rstrip("/") + "/" if "/" in tail else "/"
SELF = "chaos"
NAME = "Chaos, Drawn"
TAG = ("Chaos theory in plain words — every picture drawn from the equation that makes it, "
       "and the two tools that hold up under chaos: the law of large numbers, and systems built to bend.")
TODAY = date.today().isoformat()
FLEET = fleet.load(ROOT / "data" / "fleet.json")
FACTS = json.loads((BUILD / "facts.json").read_text(encoding="utf-8"))
FIGS = json.loads((BUILD / "figs.json").read_text(encoding="utf-8"))
CREDIT = "Nan · hongdam.net · CC BY 4.0"
E = html.escape

# the explainer siblings a reader of this page would want next
SIB = ("three-body", "black-holes", "quantum-computing", "factoring", "exceptional-magic")

NAV = [("one/", "The one idea"), ("map/", "The map"), ("weather/", "Weather"),
       ("large-numbers/", "Large numbers"), ("resilience/", "Resilience"),
       ("code/", "Code"), ("words/", "Words"), ("sources/", "Sources")]

EXTRA = """
.reading{max-width:44rem;margin:.1rem 0 1.2rem;color:var(--ink);font-size:1rem}
.reading b{color:var(--gold);font-weight:700}
.eq var{font-style:italic}
.eq sub{font-size:.7em}
.eq .op{color:var(--mute);padding:0 .12em}
.win{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--hot);
 border-radius:12px;padding:1rem 1.1rem;margin:1.3rem 0;background-image:radial-gradient(120% 100% at 0% 0%,color-mix(in srgb,var(--hot) 12%,transparent),transparent 60%)}
.win h3{margin-top:.1rem}
.win p{max-width:none}
.srclist{padding-left:1.6rem;max-width:52rem}
.srclist li{margin:.5rem 0;font-size:.9rem;line-height:1.5;color:var(--ink)}
.srclist li a{color:var(--blue);text-decoration:none}
.dial{display:grid;grid-template-columns:auto 1fr;gap:.2rem 1rem;max-width:44rem;margin:1rem 0;font-size:.95rem}
.dial dt{font-family:var(--display);font-weight:800;color:var(--hot);text-transform:uppercase;font-size:.8rem;letter-spacing:.06em;padding-top:.35rem}
.dial dd{margin:0;padding:.25rem 0;border-bottom:1px solid var(--line)}
figure.fig svg{display:block;width:100%;height:auto}
.next{display:flex;justify-content:space-between;gap:1rem;margin:2.4rem 0 0;flex-wrap:wrap}
.next a{font-family:var(--display);font-weight:800;text-transform:uppercase;letter-spacing:.04em;text-decoration:none;
 border:1px solid var(--line);padding:.6rem 1rem;border-radius:99px;color:var(--ink)}
.next a:hover{border-color:var(--hot);color:var(--hot)}
"""


def u(path=""):
    return BASE + path


def head(title, desc, path):
    canon = SITE_URL + "/" + path
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{E(canon)}">
<meta property="og:type" content="website"><meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{E(canon)}">
<meta property="og:image" content="{SITE_URL}/card.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:site_name" content="{E(NAME)}"><meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{E(title)}"><meta name="twitter:description" content="{E(desc)}">
<meta name="twitter:image" content="{SITE_URL}/card.jpg">
<meta name="theme-color" content="#07070b">
<link rel="icon" href="{u('icon.svg')}" type="image/svg+xml">
<style>{CSS}{EXTRA}</style></head><body>
<a class="sr" href="#main">Skip to the content</a>
<header class="top"><div class="in">
<a class="brand" href="{u()}"><i></i>Chaos, <b>Drawn</b></a>
<nav aria-label="Chapters">{"".join(f'<a href="{u(h)}"{" aria-current=page" if path.rstrip("/")+"/"==h else ""}>{E(t)}</a>' for h,t in NAV)}</nav>
</div></header><main id="main">"""


def foot():
    row = fleet.row_html(SELF, label="More from the same shelf", roster=FLEET, ids=SIB)
    more = fleet.row_html(SELF, label="Also from NaNoBotCo", roster=FLEET)
    support = fleet.support_html(roster=FLEET, self_id=SELF)
    maker = fleet.maker_html(roster=FLEET)
    return f"""</main><footer class="bot"><div class="in">
<p><b>{E(NAME)}</b> — {E(TAG)}</p>
<p class="small">Text and pictures CC BY 4.0. The code that draws them is MIT. Every figure is
computed by <a href="{u('code/')}">the code on this site</a>; nothing here is a stock image.
Built {E(TODAY)}.</p>
{row}
{more}
{support}
{maker}
</div></footer></body></html>"""


def cite(*ids):
    return S.cite(*ids, root=BASE)


def eq(body, reading=""):
    r = f'<p class="reading"><b>Reading it:</b> {reading}</p>' if reading else ""
    return f'<div class="eq">{body}</div>{r}'


def fig(key, caption, label=""):
    svg = FIGS[key]
    cap = f"<b>{label}.</b> {caption}" if label else caption
    return (f'<figure class="fig dark">{svg}'
            f'<figcaption>{cap} <span class="small">· computed here · {CREDIT}</span></figcaption></figure>')


def slab(cells):
    out = []
    for v, l in cells:
        if isinstance(v, tuple):
            v = f"{E(str(v[0]))}<small>{E(v[1])}</small>"
        else:
            v = E(str(v))
        out.append(f"<div><b>{v}</b><span>{E(l)}</span></div>")
    return '<div class="slab">' + "".join(out) + "</div>"


def toc(items):
    return '<div class="toc">' + "".join(f'<a href="{u(h)}">{E(t)}</a>' for h, t in items) + "</div>"


def nextlink(prev=None, nxt=None):
    a = f'<a href="{u(prev[0])}">← {E(prev[1])}</a>' if prev else "<span></span>"
    b = f'<a href="{u(nxt[0])}">{E(nxt[1])} →</a>' if nxt else "<span></span>"
    return f'<div class="next">{a}{b}</div>'


def write(path, s):
    p = SITE / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")


# ============================================================================ pages
def page_home():
    lam = FACTS["lyapunov"]
    body = f"""
<h1><span class="kind">Chaos theory, drawn</span>A small nudge,<br>a whole new world</h1>
<p class="lede">Chaos is not disorder, and it is not hard. It is what a plain, exact rule does
when a tiny change in where you start turns into a large change in where you end up. Weather does
it. A dripping tap does it. A herd, a market, a creek in spring. This page draws every bit of it
from the equations — and then hands you the two tools that let you stand in the middle of it and
still get on with your life.</p>

{slab([((lam, " /s"), "how fast tiny errors grow in the weather model"),
       ("4.669", "the number that shows up in every road to chaos"),
       (FACTS["dice_final"], "average of 3,000 die rolls — the law of large numbers at work"),
       ((f"{FACTS['rms_drift']}→{FACTS['rms_held']}", ""), "a shock, before and after one feedback loop")])}

<div class="win">
<h3>The whole idea in four sentences</h3>
<p>A <strong>chaotic</strong> system follows a fixed rule with no dice in it, so in principle its
future is set. But two starts too close to tell apart drift apart fast, so in practice you cannot
see far ahead. That is the catch, and it is the whole of it. The rest of this site is what the
catch looks like, why it happens, and what to do about it.</p>
</div>

<h2>Walk it in order</h2>
{toc([("one/","1 · The one idea"),("map/","2 · One rule into chaos"),("weather/","3 · Weather & the butterfly"),
      ("large-numbers/","4 · Tool one: large numbers"),("resilience/","5 · Tool two: build to bend"),
      ("code/","6 · Do it yourself")])}

<div class="pair">
{fig("bifurcation", "One equation, every setting at once. Turn the knob left to right and a single steady value splits to two, to four, and then into a fog — that fog is chaos.")}
{fig("lorenz", "The Lorenz weather model, traced out in the air. The line never crosses itself and never repeats, yet it stays on these two wings the whole way.")}
</div>

<h2>The part most people miss</h2>
<p>Chaos gets sold as a reason to throw up your hands. It is the opposite. Once you know a system is
chaotic, you stop wasting effort on predicting the one thing you cannot predict, and you spend it
on the two things that work every time.</p>
<div class="two">
<div class="win"><h3>Count the many, not the one</h3>
<p>You cannot say how one die lands. You can say, to a hair, what a thousand of them average. Chaos
lives in the single case; order lives in the pile. That is the <a href="{u('large-numbers/')}">law of
large numbers</a>, and it is a tool you can pick up.</p></div>
<div class="win"><h3>Build it to bend</h3>
<p>You cannot stop the shock you did not see coming. You can build the thing that takes it: give it
slack, give it spares, spread its bets, and wire in something that pulls it back to centre. That is
a <a href="{u('resilience/')}">resilient system</a>, and it is the second tool.</p></div>
</div>

{nextlink(nxt=("one/", "The one idea"))}
"""
    write("index.html", head(NAME, TAG, "") + body + foot())


def page_one():
    body = f"""
<h1><span class="kind">Chapter 1</span>The one idea</h1>
<p class="lede">A hair's difference at the start, a canyon's difference at the end. Everything else
about chaos is a detail hanging off this one fact.</p>

<h2>Two creeks off the same ridge</h2>
<p>Rain lands on a ridge. Two drops fall a finger apart. One slides left of a stone, one slides
right, and by the valley floor they are in different rivers, different towns, different seas. The
ridge did nothing strange. The rule — water runs downhill — is as plain as a rule gets. The drops
just started on two sides of a line, and the hill did the rest.</p>
<p>That is chaos, and here it is in numbers. Take the simplest rule that folds a line back on
itself, feed it two starting values a ten-thousandth apart, and watch.</p>

{eq('<var>x</var><sub>next</sub> <span class="op">=</span> <var>r</var> <span class="op">·</span> <var>x</var> <span class="op">·</span> (1 <span class="op">−</span> <var>x</var>)',
    'take where you are (<var>x</var>, a number between 0 and 1), multiply by a growth knob <var>r</var>, '
    'and multiply again by how much room is left (1 − <var>x</var>). That is next year. Do it again for the year after.')}

{fig("creeks", f"Both lines obey the same rule with the same knob (r = {FACTS['r_creek']}). They start a ten-thousandth apart, track each other for a while, and by step {FACTS['split_step']} they have nothing to do with each other.", "Fig 1")}

<p>Nobody added randomness. Run it twice from the same start and you get the same line to the last
decimal. The two lines split only because they began a whisker apart — and the whisker doubled, and
doubled, until it was the whole width of the picture.</p>

<h2>Why the gap grows: stretch and fold</h2>
<p>Look at the rule as a motion. The <var>r·x</var> part <strong>stretches</strong> the line — pulls
neighbours apart. The <var>(1 − x)</var> part <strong>folds</strong> it back so nothing escapes past
1. Stretch, fold, stretch, fold: it is taffy on a hook, or a deck shuffled and shuffled. Two grains
of sugar side by side in the taffy are soon a whole pull apart, though never off the ends.<sup class="src"><a href="{u('sources/')}#smale1967">13</a></sup></p>
<p>Every chaotic system on this site is doing exactly this — stretching in one direction, folding to
stay in bounds. That is the engine. The rest is watching it run.</p>

<div class="win"><h3>Chaos is not randomness</h3>
<p>A coin is random: no rule inside it tells you the next flip. A chaotic system is the reverse — the
rule is complete and exact, and still you cannot see far ahead, because you can never write the
starting number down with enough decimals. Determined, and unpredictable, at the same time. Hold
those two words together and you have understood the thing.</p></div>

{nextlink(("", "Home"), ("map/", "One rule into chaos"))}
"""
    write("one/index.html", head("The one idea — " + NAME, "Sensitive dependence on initial conditions, drawn: a hair's difference at the start becomes a canyon at the end.", "one/") + body + foot())


def page_map():
    d = FACTS["doublings"]
    fg = FACTS["feigenbaum_all"]
    body = f"""
<h1><span class="kind">Chapter 2</span>One rule into chaos</h1>
<p class="lede">The rule from chapter one has a single knob. Turn it slowly and the same equation goes
from dead calm, to a steady beat, to a flutter, to chaos — and it tells you exactly where the door
is.</p>

<h2>A rabbit rule</h2>
<p>Robert May, a biologist, wrote this rule down in 1976 for a herd that breeds and then runs short
of grass.<sup class="src"><a href="{u('sources/')}#may1976">7</a></sup> The knob <var>r</var> is how
fast they breed. Small <var>r</var>: the herd finds a size and holds it. Turn <var>r</var> up and
something strange starts to happen.</p>

<div class="three">
{fig("cobweb_calm", "Low knob. The herd climbs to one size and sits there. Every path leads to the same corner.", "2a")}
{fig("cobweb_two", "Higher knob. Now it can't sit still — it swings high year, low year, high year, forever. A two-beat.", "2b")}
{fig("cobweb_chaos", "Higher still. The path never lands twice in the same place. It fills the box.", "2c")}
</div>
<p class="mute small">How to read these: the hill is the rule, the straight diagonal is “next year equals
this year”. Bounce between them — up to the hill, across to the diagonal, up to the hill — and you
are stepping the herd forward one year at a time.</p>

<h2>The whole family, on one page</h2>
<p>Instead of picking one knob setting, draw them all. Left to right is the knob. Top to bottom, for
each setting, are the sizes the herd settles into after the fuss dies down.</p>

{fig("bifurcation", "One steady size, then a fork to two, then to four, then a smear where the count is beyond counting. The forks come faster and faster until they pile up at a wall — and past the wall is chaos.", "Fig 3")}

<p>Read it like a river seen from above. For a while there is one channel. It splits to two, the two
split to four, four to eight — each split closer to the last — and then the banks dissolve. The
place where they dissolve is not vague; it is a specific number, near <strong>3.5699</strong>.</p>

<h2>The number hiding in the forks</h2>
<p>Measure where each fork happens and something turns up that nobody put there. The forks on this
run land at:</p>
<dl class="dial">
<dt>1 → 2</dt><dd>r = {d[0]}</dd>
<dt>2 → 4</dt><dd>r = {d[1]}</dd>
<dt>4 → 8</dt><dd>r = {d[2]}</dd>
<dt>8 → 16</dt><dd>r = {d[3]}</dd>
</dl>
<p>Now take the gaps between forks and divide each by the next. On this run that ratio comes out
{fg[0]}, then {fg[1]} — closing in on a fixed number:</p>

{eq('<var>δ</var> <span class="op">=</span> 4.669 201 609 …',
    'each fork sits about 4.669 times closer to the wall than the fork before it. Mitchell Feigenbaum '
    'found this same number in the logistic map, in a dripping tap, in a heart — in every rule shaped '
    'like a single hill. It does not care what the system is made of.')}

<p>That is the quiet shock of chaos theory. The road into it has a shape, and the shape is the same
for things that share nothing else.<sup class="src"><a href="{u('sources/')}#feigenbaum1978">9</a></sup></p>

<h2>And inside the chaos, calm</h2>
{fig("bifurcation_zoom", "Zoom into a slice of the fog and clear bands open up — here the herd falls into a clean three-year cycle before smearing out again. Chaos has windows of order inside it, at every scale.", "Fig 4")}
<p>The three-year window is famous. In 1975 Li and Yorke proved that any rule of this kind which can
produce a three-beat can produce a cycle of <em>every</em> length, and a tangle that never repeats
at all. Their title gave the field its name: <em>Period Three Implies Chaos</em>.<sup class="src"><a href="{u('sources/')}#liyorke1975">8</a></sup></p>

{nextlink(("one/", "The one idea"), ("weather/", "Weather & the butterfly"))}
"""
    write("map/index.html", head("One rule into chaos — " + NAME, "The logistic map, drawn: period doubling, the bifurcation tree, and Feigenbaum's 4.669 found in the forks.", "map/") + body + foot())


def page_weather():
    lam = FACTS["lyapunov"]
    hz = FACTS["horizon"]
    body = f"""
<h1><span class="kind">Chapter 3</span>Weather & the butterfly</h1>
<p class="lede">In 1961 a weather researcher rounded three numbers off at the third decimal to save
paper, ran the forecast again, and got a different season. That accident is why the ten-day forecast
will never come.</p>

<h2>Three equations for a sky</h2>
<p>Edward Lorenz stripped a weather model down to three numbers — how fast the air rolls, and two
about how the heat sits — and three rules for how they push each other.<sup class="src"><a href="{u('sources/')}#lorenz1963">5</a></sup>
No noise, no dice. He expected it to settle or to loop. It did neither.</p>

{eq('<var>ẋ</var> <span class="op">=</span> <var>σ</var>(<var>y</var> − <var>x</var>) &nbsp;&nbsp; '
    '<var>ẏ</var> <span class="op">=</span> <var>x</var>(<var>ρ</var> − <var>z</var>) − <var>y</var> &nbsp;&nbsp; '
    '<var>ż</var> <span class="op">=</span> <var>xy</var> − <var>βz</var>',
    'the little dot means “rate of change”. Each line says how fast one number moves given where all '
    'three are now. Feed in a start, take tiny steps, and the three numbers trace a path through the air.')}

{fig("lorenz", "The path those three rules draw, with Lorenz's own settings. It circles one wing, jumps to the other, circles a few times, jumps back — the order of the jumps never repeating. This shape is a strange attractor: every start is pulled onto it, and no start ever settles down on it.", "Fig 5")}

<h2>Round off at the third decimal, lose the month</h2>
<p>Here is Lorenz's accident, on purpose. Two runs of the same three equations, one started a
hundred-thousandth away from the other in a single number.</p>

{fig("forecast", "For a good while the two forecasts are one line — you could not slip a knife between them. Then they part, and within a day or two one says storm and the other says clear. Same equations. Same knob. A rounding error at the start.", "Fig 6")}

<h2>How far ahead can anyone see?</h2>
<p>This is the part you can actually measure. Track the gap between the two runs and plot it on a
scale where each step up is ten times bigger. The gap climbs a straight line — meaning it multiplies
by a fixed factor every second — until it is as wide as the whole butterfly and cannot grow more.</p>

{fig("lyapunov_fig", f"The gap grows by a steady factor, the same factor every second. The slope of that climb is the Lyapunov exponent, λ ≈ {lam} per second here. It is the single number that says how chaotic a system is.", "Fig 7")}

{eq('gap(<var>t</var>) <span class="op">≈</span> gap(0) <span class="op">·</span> <var>e</var><sup><var>λt</var></sup>',
    f'the gap you start with, times a number that doubles and redoubles on the clock. With λ ≈ {lam}, '
    f'the gap grows about {round(2.718**lam,1)}-fold every second of model time.')}

<p>Turn it around and you get the forecast horizon. To keep the gap useful you must start with it
this much smaller — so every extra decimal of accuracy in your measurements buys you only a
<em>fixed</em> stretch more warning, not a proportional one. Ten times better instruments push the
horizon out by the same short step as the ten times before them. On this model that step is about
<strong>{hz} seconds</strong> of model time per factor of ten.</p>

<div class="win"><h3>Why the weather app stops at ten days</h3>
<p>The real atmosphere has a doubling time for small errors of roughly a day and a half. Start with
the best measurements on Earth and the unknown in them still grows to swamp the forecast in about
two weeks. Better satellites help — but only by that same fixed step each time. Two weeks is not a
budget problem. It is the Lyapunov wall.<sup class="src"><a href="{u('sources/')}#lorenz1972">6</a></sup></p></div>

{nextlink(("map/", "One rule into chaos"), ("large-numbers/", "Tool one: large numbers"))}
"""
    write("weather/index.html", head("Weather & the butterfly — " + NAME, "The Lorenz attractor drawn from its three equations, the forecast horizon, and the Lyapunov exponent measured on this machine.", "weather/") + body + foot())


def page_large():
    df = FACTS["dice_final"]
    body = f"""
<h1><span class="kind">Chapter 4 · Tool one</span>The law of large numbers</h1>
<p class="lede">You cannot call one die. You can call a thousand of them cold. Chaos hides in the single
throw; certainty is waiting in the pile. This is the first tool for living with chaos, and it is
older than the word.</p>

<h2>One die, three thousand times</h2>
<p>A fair die is close enough to unpredictable for anyone's purpose — you will not call the next face.
But keep a running average of the faces as you roll, and something firm happens.</p>

{fig("dice", f"The running average staggers around early — a couple of high rolls and it lurches up — then it is reeled in, tighter and tighter, to 3.5. After 3,000 rolls this run sat at {df}. The shaded funnel is how far off you should expect to be, and it closes like 1 over the square root of the number of rolls.", "Fig 8")}

{eq('<span style="display:inline-block;vertical-align:middle">average of <var>N</var> rolls</span> '
    '<span class="op">→</span> <var>μ</var>, &nbsp; with a spread of about <var>σ</var> / √<var>N</var>',
    'as the count <var>N</var> climbs, the average closes on the true mean <var>μ</var> (3.5 for a die), '
    'and the wobble around it shrinks as one over the square root of <var>N</var>. Four times the rolls, '
    'half the wobble.')}

<p>Jacob Bernoulli proved this in a book published in 1713, and was proud enough to call it his golden
theorem.<sup class="src"><a href="{u('sources/')}#bernoulli1713">16</a></sup> It is the ground under
every poll, every insurance premium, every casino floor. None of them can call the one. All of them
can call the many, and they bet the building on it.</p>

<h2>The bridge back to chaos</h2>
<p>Here is where it gets good. Take the most chaotic rule on this whole site — the rabbit map with
its knob turned all the way to 4, the one whose path never repeats and cannot be forecast a dozen
steps out. You cannot say what its next value will be. But drop three hundred thousand of its values
into bins and count them.</p>

{fig("invariant", "The single values are unforecastable. The pile they make is a fixed, exact curve — more time spent near the ends, less in the middle — and it is the same curve every run, 1 over π times the square root of x(1−x).", "Fig 9")}

<p>The individual step: chaos, no forecast. The long-run shape: a law, down to the decimals, known
in closed form since von Neumann used this very map to make random numbers in 1947.<sup class="src"><a href="{u('sources/')}#ulamvonneumann1947">15</a></sup>
That is the tool in one picture. <strong>When you cannot predict the case, predict the
distribution.</strong> Stop asking which way this one falls and ask how the whole heap settles — the
heap holds still even when every grain in it is jumping.</p>

<div class="win"><h3>How to pick it up</h3>
<p>Do not forecast the customer; forecast the month. Do not time the one trade; hold the many. Do not
ask whether it rains Tuesday; ask how many wet days the season brings — that number barely moves. The
law of large numbers turns a wall of chaos into a fact you can plan around, as long as you are willing
to zoom out from the one to the many.</p></div>

{nextlink(("weather/", "Weather & the butterfly"), ("resilience/", "Tool two: build to bend"))}
"""
    write("large-numbers/index.html", head("The law of large numbers — " + NAME, "Chaos in the single throw, certainty in the pile: the law of large numbers, and a chaotic map whose long-run shape is an exact curve.", "large-numbers/") + body + foot())


def page_resilience():
    rd, rh = FACTS["rms_drift"], FACTS["rms_held"]
    body = f"""
<h1><span class="kind">Chapter 5 · Tool two</span>Build it to bend</h1>
<p class="lede">You cannot predict the shock. You can build the thing that takes it and keeps going.
A resilient system does not need to see the future — it is shaped so the future cannot break it.
Four moves, each one drawn.</p>

<h2>Move one — pull back to centre</h2>
<p>The oldest trick in engineering: measure how far off you are and push back a share of it, every
tick. A woodstove with a thermostat. A hand on a wheel on a washboard road. James Clerk Maxwell wrote
the mathematics of it in 1868 and started a whole field.<sup class="src"><a href="{u('sources/')}#maxwell1868">20</a></sup></p>

{fig("governor", f"Two tanks take the very same run of random shocks. One just piles them up and wanders off (it drifted to {rd} from centre). The other subtracts a fraction of its own error every step and stays put (it held to {rh}). Same shocks. One rule of feedback between them.", "Fig 10")}

{eq('error<sub>next</sub> <span class="op">=</span> (1 − <var>k</var>) <span class="op">·</span> error<sub>now</sub>',
    'each step, keep only the fraction (1 − <var>k</var>) of the error you had. As long as the pull-back '
    '<var>k</var> is between 0 and 2, the error dies away on its own. Pull too hard, past 2, and you '
    'overshoot worse each time — feedback wired backwards makes its own chaos.')}

<h2>Move two — keep spares</h2>
<p>If one part fails one time in ten, two that fail on their own both fail only one time in a hundred;
three, one in a thousand. Independence is a fierce multiplier — <em>if</em> you can keep it.</p>

{fig("redundancy", "The straight drop is the dream: each spare cuts the failure rate ten-fold. The two dashed lines are the catch — let a common cause reach across your spares (one power feed, one supplier, one bad assumption) and the floor stops falling. Redundancy is only worth what its independence is worth.", "Fig 11")}

{eq('P(all <var>N</var> fail) <span class="op">=</span> <var>p</var><sup><var>N</var></sup> &nbsp; '
    '<span class="mute">(only if they fail independently)</span>',
    'the chance every one of <var>N</var> parts fails at once is the single-part chance multiplied by '
    'itself <var>N</var> times — a tiny number, fast. The parenthesis is the whole ballgame: shared '
    'causes break the multiplication.')}

<h2>Move three — spread the bet</h2>
<p>This is the law of large numbers from chapter four, put to work on purpose. Split a stake across
many independent bets and the swing shrinks as one over the square root of their number — same
expected return, less lurch. Harry Markowitz won a Nobel for writing this down plainly in 1952.<sup class="src"><a href="{u('sources/')}#markowitz1952">18</a></sup></p>

{fig("portfolio", "Spread across independent bets and the swing keeps falling. But the moment the bets share a common risk — one market, one weather, one rumour — the fall stops at a floor no further spreading can get under. That floor is the shared risk, and only a different kind of bet removes it.", "Fig 12")}

<h2>Move four — stay off the edge</h2>
<p>Chapter two showed a wall where a steady system tips into chaos, with the forks crowding up to it.
A resilient system is run with room to that wall, not parked against it for the last drop of yield. C.
S. Holling, studying forests and fisheries, drew the line between two things people muddle: how fast a
system springs back, and how big a shock it can take before it flips to a different world
entirely.<sup class="src"><a href="{u('sources/')}#holling1973">19</a></sup> Slack is what buys the
second one. A system with no slack is fast and efficient right up until the day it is neither.</p>

<div class="win"><h3>The tool, in one line each</h3>
<p><strong>Pull back to centre</strong> — wire in something that corrects error on its own.<br>
<strong>Keep spares</strong> — and guard their independence harder than the spares themselves.<br>
<strong>Spread the bet</strong> — many small uncorrelated exposures beat one big right guess.<br>
<strong>Stay off the edge</strong> — keep margin to the tipping point; measure the shock you can take,
not only the speed you bounce back.</p>
<p class="mute">None of these needs a forecast. That is the point. You are not trying to out-guess the
chaos. You are building something that does not need to.</p></div>

{nextlink(("large-numbers/", "Tool one: large numbers"), ("code/", "Do it yourself"))}
"""
    write("resilience/index.html", head("Build it to bend — resilient systems — " + NAME, "Four drawn moves for standing up to chaos you cannot predict: negative feedback, redundancy, diversification, and margin to the tipping point.", "resilience/") + body + foot())


CODE = '''#!/usr/bin/env python3
"""chaos.py — the whole site's mathematics, no libraries, runs in a second.

    python3 chaos.py

Prints: a chaotic run you can't forecast, the average of a chaotic pile that never moves,
the weather model's Lyapunov exponent, and one feedback loop taming a run of shocks.
"""
import math, random


def logistic(r, x, n):
    "The rabbit rule: where you are, times the growth knob, times the room left."
    for _ in range(n):
        x = r * x * (1 - x)
        yield x


def lorenz_step(s, dt=0.006, sig=10, rho=28, beta=8/3):
    x, y, z = s
    def d(st):
        x, y, z = st
        return (sig*(y-x), x*(rho-z)-y, x*y-beta*z)
    k1 = d(s)
    k2 = d((x+dt/2*k1[0], y+dt/2*k1[1], z+dt/2*k1[2]))
    k3 = d((x+dt/2*k2[0], y+dt/2*k2[1], z+dt/2*k2[2]))
    k4 = d((x+dt*k3[0],   y+dt*k3[1],   z+dt*k3[2]))
    return tuple(s[i] + dt/6*(k1[i]+2*k2[i]+2*k3[i]+k4[i]) for i in range(3))


def lyapunov(dt=0.006, n=60000, d0=1e-9):
    "Benettin's method: run a twin a hair away, measure the growth, pull it back, repeat."
    a = (1.0, 1.0, 1.0)
    for _ in range(4000):            # settle onto the attractor
        a = lorenz_step(a, dt)
    b = (a[0]+d0, a[1], a[2])
    total = 0.0
    for _ in range(n):
        a, b = lorenz_step(a, dt), lorenz_step(b, dt)
        gap = math.dist(a, b)
        total += math.log(gap/d0)
        f = d0/gap                   # rescale the twin back to distance d0
        b = (a[0]+(b[0]-a[0])*f, a[1]+(b[1]-a[1])*f, a[2]+(b[2]-a[2])*f)
    return total/(n*dt)


def die_average(n, seed=70118):
    rng = random.Random(seed)
    s = 0
    for i in range(1, n+1):
        s += rng.randint(1, 6)
    return s/n


def governor(k=0.28, n=240, seed=4669):
    "One feedback loop against a run of shocks: subtract k of the error each step."
    rng = random.Random(seed)
    drift = held = 0.0
    for _ in range(n):
        shock = rng.gauss(0, 1) * 0.5
        drift += shock                       # no correction
        held += shock; held -= k * held      # pull back k of the error
    return drift, held


if __name__ == "__main__":
    run = list(logistic(4.0, 0.4, 12))
    print("chaotic run (unforecastable):", " ".join(f"{v:.3f}" for v in run))

    pile = list(logistic(4.0, 0.31415926, 300000))
    print("average of 300,000 chaotic values:", round(sum(pile)/len(pile), 4), "(theory 0.5)")

    print("Lyapunov exponent of the weather model:", round(lyapunov(), 3), "(known 0.906)")

    print("die average over 3,000 rolls:", round(die_average(3000), 3), "(true 3.5)")

    drift, held = governor()
    print(f"shock left alone drifted to {drift:.2f}; one feedback loop held it to {held:.2f}")
'''


def page_code():
    body = f"""
<h1><span class="kind">Chapter 6</span>Do it yourself</h1>
<p class="lede">Every picture on this site comes out of a few lines of plain Python with nothing
imported but the standard library. Here is the heart of it. Copy it, run it, change the numbers,
break it.</p>

<p><a class="btn solid" href="{u('chaos.py')}" download>Download chaos.py</a> &nbsp;
<a class="btn" href="https://github.com/NaNoBotCo/chaos">The full source on GitHub</a></p>

<pre><code>{E(CODE)}</code></pre>

<h2>What it prints</h2>
<p>Run <code>python3 chaos.py</code> and you get, in order: a dozen steps of the fully chaotic rabbit
map (you will not be able to forecast the thirteenth); the average of three hundred thousand of those
same chaotic values, which sits on 0.5 every time; the weather model's Lyapunov exponent, measured
the way chapter three measured it, landing near the textbook 0.906; the average of three thousand die
rolls, near 3.5; and a single feedback loop pulling a run of shocks back to centre.</p>
<p>Six functions, one file, no dependencies. The chaos, the two tools, and the proof that the pile
holds still while the grains jump — all of it fits on a page.</p>

<div class="win"><h3>Things worth breaking</h3>
<p>Change the logistic knob from 4.0 to 3.5 and watch the “chaotic” run turn into a clean four-beat.
Set the governor pull-back <code>k</code> above 2 and watch the correction overshoot into its own
chaos. Widen the twin's head start <code>d0</code> and see the Lyapunov number barely budge — it is a
property of the system, not of how you poke it.</p></div>

{nextlink(("resilience/", "Tool two: build to bend"), ("words/", "The words"))}
"""
    write("code/index.html", head("Do it yourself — the code — " + NAME, "The mathematics behind every figure, in a few lines of dependency-free Python you can run and change.", "code/") + body + foot())
    write("chaos.py", CODE)


WORDS = [
    ("Chaos", "A system that follows a fixed rule with no randomness in it, yet cannot be forecast far ahead, because starts too close to tell apart pull rapidly apart."),
    ("Sensitive dependence on initial conditions", "The plain name for the above: a tiny change in where you start becomes a large change in where you end. The “butterfly effect”."),
    ("Deterministic", "Set by a rule, with no dice. Run it twice from the same start and you get the same answer. Chaotic systems are deterministic — that is what makes them surprising."),
    ("Logistic map", "The rule x → r·x·(1−x). A herd that breeds and runs short of grass. The simplest thing that goes chaotic, and the workhorse of this site."),
    ("Bifurcation", "A fork: a place where turning the knob a hair splits one steady behaviour into two. Stack enough forks close together and you reach chaos."),
    ("Period doubling", "The particular road the logistic map takes into chaos — one beat, two, four, eight — each fork closer than the last."),
    ("Feigenbaum constant", "4.669… — the fixed ratio by which those forks crowd together, the same for a whole class of systems that share nothing else."),
    ("Attractor", "The shape a system is drawn onto and then stays on, whatever start you pick. A resting point, a loop, or —"),
    ("Strange attractor", "— an attractor that never repeats and has structure at every scale, like the Lorenz butterfly. The signature of chaos in a flow."),
    ("Lorenz system", "Three equations Edward Lorenz reduced weather to in 1963; the first clear example of chaos in a physical model."),
    ("Lyapunov exponent", "The single number λ that says how fast nearby paths separate. Positive means chaos; bigger means less warning. Its reciprocal is roughly how far ahead you can see."),
    ("Stretch and fold", "The two motions under every chaotic map: pull neighbours apart, then fold the whole thing back to stay in bounds. Taffy on a hook."),
    ("Law of large numbers", "As you pile up independent trials, their average closes on the true mean and its wobble shrinks as one over the square root of the count. The first tool for living with chaos."),
    ("Invariant distribution", "The fixed shape the values of a chaotic map settle into over the long run, even though each single value is unforecastable. Chaos in the one, law in the many."),
    ("Resilience", "How large a shock a system can take and still recover its shape — as distinct from how fast it bounces back. The second tool."),
    ("Negative feedback", "Measuring your error and pushing back a share of it, every step. The move that keeps a system near its centre without anyone forecasting the shocks."),
    ("Redundancy", "Spare parts that can each do the job, so the whole survives any one failing — worth exactly as much as the parts' independence."),
    ("Diversification", "Spreading a stake across many uncorrelated bets so the swing shrinks without the return shrinking. The law of large numbers, used on purpose."),
    ("Tipping point", "The knob setting where a system flips from one world to another — steady to chaotic, lake to swamp. Resilience is margin to this edge."),
]


def page_words():
    rows = "".join(f'<dt>{E(t)}</dt><dd>{d}</dd>' for t, d in sorted(WORDS))
    body = f"""
<h1><span class="kind">Glossary</span>The words</h1>
<p class="lede">Every term on this site, in one place, in plain language. {len(WORDS)} of them.</p>
<dl class="dial">{rows}</dl>
{nextlink(("code/", "Do it yourself"), ("sources/", "Sources"))}
"""
    write("words/index.html", head("The words — " + NAME, "A plain-language glossary of chaos theory: sensitive dependence, attractors, Lyapunov exponents, the law of large numbers, resilience.", "words/") + body + foot())


def page_sources():
    body = f"""
<h1><span class="kind">Sources</span>Where this comes from</h1>
<p class="lede">{len(S.SOURCES)} sources — the papers that built the field, and the books to read next.
Every claim on this site traces to one of these; every figure is computed by
<a href="{u('code/')}">the code</a>, not taken from them.</p>
{S.render_list(root=BASE)}
{nextlink(("words/", "The words"), ("", "Home"))}
"""
    write("sources/index.html", head("Sources — " + NAME, "The papers and books behind the site, from Poincaré and Lorenz to Feigenbaum, Bernoulli, Markowitz and Holling.", "sources/") + body + foot())


# ============================================================================ machine files
ICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#07070b"/><path d="M6 40 C 18 40 18 16 30 16 C 42 16 42 48 54 48" fill="none" stroke="#ffb347" stroke-width="4" stroke-linecap="round"/><circle cx="30" cy="16" r="3.4" fill="#8fd0ff"/><circle cx="6" cy="40" r="3" fill="#ff6a5e"/></svg>'''


def page_404():
    body = """
<h1><span class="kind">404</span>No such page</h1>
<p class="lede">Small change, big difference — you started one letter off and ended up here.</p>
<p><a class="btn solid" href="%s">Back to the start</a></p>
""" % u()
    write("404.html", head("Not found — " + NAME, "Page not found.", "404.html") + body + foot())


def machine_files():
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    (SITE / ".basepath").write_text(BASE + "\n", encoding="utf-8")
    (SITE / "icon.svg").write_text(ICON + "\n", encoding="utf-8")
    (SITE / "manifest.webmanifest").write_text(json.dumps({
        "name": NAME, "short_name": "Chaos", "start_url": BASE, "display": "standalone",
        "background_color": "#07070b", "theme_color": "#07070b",
        "icons": [{"src": u("icon.svg"), "sizes": "any", "type": "image/svg+xml"}]}, indent=2) + "\n", encoding="utf-8")

    pages = ["", "one/", "map/", "weather/", "large-numbers/", "resilience/", "code/", "words/", "sources/"]
    urls = "".join(f"<url><loc>{SITE_URL}/{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in pages)
    (SITE / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n',
        encoding="utf-8")

    (SITE / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")

    (SITE / "llms.txt").write_text(
        f"# {NAME}\n\n> {TAG}\n\n"
        f"Chaos theory, drawn from the equations. Sensitive dependence, the logistic map and its road "
        f"into chaos, the Lorenz attractor and the forecast horizon, and then the two tools for living "
        f"with chaos: the law of large numbers, and resilient systems (feedback, redundancy, "
        f"diversification, margin to the tipping point). Every figure is computed by the site's own code.\n\n"
        f"## Pages\n"
        f"- [The one idea]({SITE_URL}/one/): sensitive dependence on initial conditions.\n"
        f"- [One rule into chaos]({SITE_URL}/map/): the logistic map, period doubling, Feigenbaum's 4.669.\n"
        f"- [Weather & the butterfly]({SITE_URL}/weather/): the Lorenz attractor and the Lyapunov exponent.\n"
        f"- [The law of large numbers]({SITE_URL}/large-numbers/): certainty in the pile.\n"
        f"- [Build it to bend]({SITE_URL}/resilience/): resilient systems.\n"
        f"- [The code]({SITE_URL}/code/): the mathematics in a few lines of Python.\n"
        f"- [Words]({SITE_URL}/words/) · [Sources]({SITE_URL}/sources/)\n",
        encoding="utf-8")

    (SITE / "ai.txt").write_text(
        f"Publisher: {FLEET['publisher']} · {FLEET['contact']}\nSite: {NAME} — {SITE_URL}/\n"
        f"Licence: text and figures CC BY 4.0; code MIT.\n", encoding="utf-8")

    (SITE / "humans.txt").write_text(
        f"/* {NAME} */\n{TAG}\n\nBuilt {TODAY}. Figures computed by tools/figures.py.\n"
        f"Text & figures CC BY 4.0 · code MIT.\n", encoding="utf-8")

    touched = fleet.decorate(SITE, SELF, roster=FLEET)
    return touched


def build_all():
    SITE.mkdir(parents=True, exist_ok=True)
    page_home(); page_one(); page_map(); page_weather()
    page_large(); page_resilience(); page_code(); page_words(); page_sources()
    page_404()
    touched = machine_files()
    n = len(list(SITE.rglob("index.html")))
    print(f"built {n} pages into {SITE}  ·  base {BASE}  ·  machine files: {', '.join(touched)}")


if __name__ == "__main__":
    build_all()
