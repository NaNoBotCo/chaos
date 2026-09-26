# -*- coding: utf-8 -*-
"""sources.py — every source the site cites, by id. A citation in the text is
cite("id"), which renders a numbered superscript link to /sources/#id."""

import html

SOURCES = [
    # ---- the mathematics of chaos
    ("poincare1890", "Henri Poincaré, “Sur le problème des trois corps et les équations de la dynamique”, Acta Mathematica 13 (1890) 1–270 — the first sight of a system whose future depends without limit on where it began.", "https://doi.org/10.1007/BF02392506"),
    ("poincare1908", "Henri Poincaré, Science et méthode (1908), book I, chapter 4: “a very small cause, which escapes us, determines a considerable effect which we cannot help seeing.”", "https://en.wikipedia.org/wiki/Butterfly_effect#History"),
    ("hadamard1898", "Jacques Hadamard, “Les surfaces à courbures opposées et leurs lignes géodésiques”, Journal de mathématiques pures et appliquées 4 (1898) 27 — nearby paths on a curved surface pulling apart exponentially.", "https://en.wikipedia.org/wiki/Hadamard%27s_dynamical_system"),
    ("lyapunov1892", "Aleksandr Lyapunov, The General Problem of the Stability of Motion (1892, doctoral thesis, Kharkov); English translation, Taylor & Francis 1992 — the exponent that measures how fast neighbours separate.", "https://en.wikipedia.org/wiki/Lyapunov_exponent"),
    ("lorenz1963", "Edward N. Lorenz, “Deterministic Nonperiodic Flow”, Journal of the Atmospheric Sciences 20 (1963) 130–141 — three equations for convection, and the discovery that they never repeat.", "https://doi.org/10.1175/1520-0469(1963)020<0130:DNF>2.0.CO;2"),
    ("lorenz1972", "Edward N. Lorenz, “Predictability: Does the Flap of a Butterfly's Wings in Brazil Set Off a Tornado in Texas?”, address to the AAAS, 29 December 1972.", "https://mathsciencehistory.com/wp-content/uploads/2020/03/132_kap6_lorenz_artikel_the_butterfly_effect.pdf"),
    ("may1976", "Robert M. May, “Simple mathematical models with very complicated dynamics”, Nature 261 (1976) 459–467 — the logistic map, and a call to teach it in schools.", "https://doi.org/10.1038/261459a0"),
    ("liyorke1975", "Tien-Yien Li & James A. Yorke, “Period Three Implies Chaos”, American Mathematical Monthly 82 (1975) 985–992 — the paper that put the word “chaos” into mathematics.", "https://doi.org/10.2307/2318254"),
    ("feigenbaum1978", "Mitchell J. Feigenbaum, “Quantitative universality for a class of nonlinear transformations”, Journal of Statistical Physics 19 (1978) 25–52 — the constant 4.669, the same for a whole class of maps.", "https://doi.org/10.1007/BF01020332"),
    ("sharkovskii1964", "Oleksandr Sharkovsky, “Co-existence of cycles of a continuous map of the line into itself”, Ukrainian Mathematical Journal 16 (1964) 61 — the ordering of periods that has period three at its head.", "https://en.wikipedia.org/wiki/Sharkovskii%27s_theorem"),
    ("ruelletakens1971", "David Ruelle & Floris Takens, “On the nature of turbulence”, Communications in Mathematical Physics 20 (1971) 167 — the phrase “strange attractor”.", "https://doi.org/10.1007/BF01646553"),
    ("mandelbrot1967", "Benoit Mandelbrot, “How Long Is the Coast of Britain? Statistical Self-Similarity and Fractional Dimension”, Science 156 (1967) 636.", "https://doi.org/10.1126/science.156.3775.636"),
    ("smale1967", "Stephen Smale, “Differentiable dynamical systems”, Bulletin of the AMS 73 (1967) 747 — the horseshoe: stretch and fold, the engine under every chaotic map.", "https://doi.org/10.1090/S0002-9904-1967-11798-1"),
    ("benettin1980", "Giancarlo Benettin, Luigi Galgani, Antonio Giorgilli & Jean-Marie Strelcyn, “Lyapunov Characteristic Exponents for smooth dynamical systems”, Meccanica 15 (1980) 9 — the method used here to measure the exponent.", "https://doi.org/10.1007/BF02128236"),
    ("ulamvonneumann1947", "Stanisław Ulam & John von Neumann, “On combination of stochastic and deterministic processes”, Bulletin of the AMS 53 (1947) 1120 — the map x → 4x(1−x) as a source of pseudo-random numbers, and its arcsine distribution.", "https://doi.org/10.1090/S0002-9904-1947-08918-7"),
    # ---- the law of large numbers
    ("bernoulli1713", "Jacob Bernoulli, Ars Conjectandi (Basel, 1713), part IV — the first proof that the observed frequency closes on the true chance as the trials pile up. His “golden theorem”.", "https://en.wikipedia.org/wiki/Law_of_large_numbers#History"),
    ("kolmogorov1933", "Andrey Kolmogorov, Grundbegriffe der Wahrscheinlichkeitsrechnung (1933); English, Foundations of the Theory of Probability, Chelsea 1956 — the strong law and the axioms under it.", "https://en.wikipedia.org/wiki/Law_of_large_numbers"),
    ("markowitz1952", "Harry Markowitz, “Portfolio Selection”, Journal of Finance 7 (1952) 77–91 — spreading a stake across uncorrelated bets shrinks the swing without shrinking the return.", "https://doi.org/10.2307/2975974"),
    # ---- resilience
    ("holling1973", "C. S. Holling, “Resilience and Stability of Ecological Systems”, Annual Review of Ecology and Systematics 4 (1973) 1–23 — resilience as the size of the shock a system can take and still recover, as distinct from how fast it returns.", "https://doi.org/10.1146/annurev.es.04.110173.000245"),
    ("maxwell1868", "James Clerk Maxwell, “On Governors”, Proceedings of the Royal Society 16 (1868) 270 — the mathematics of a machine that corrects its own error, the ancestor of control theory.", "https://doi.org/10.1098/rspl.1867.0055"),
    ("wiener1948", "Norbert Wiener, Cybernetics: or Control and Communication in the Animal and the Machine (MIT Press, 1948) — feedback as the common thread of stable systems, living and built.", "https://en.wikipedia.org/wiki/Cybernetics"),
    # ---- read further
    ("strogatz2015", "Steven H. Strogatz, Nonlinear Dynamics and Chaos, 2nd ed. (Westview/CRC, 2015) — the standard undergraduate text, and a kind one.", "https://www.stevenstrogatz.com/books/nonlinear-dynamics-and-chaos"),
    ("gleick1987", "James Gleick, Chaos: Making a New Science (Viking, 1987) — how the field came together, told for everyone.", "https://around.com/chaos/"),
    ("taleb2012", "Nassim Nicholas Taleb, Antifragile: Things That Gain from Disorder (Random House, 2012) — a working vocabulary for things that get stronger under stress, not merely survive it.", "https://en.wikipedia.org/wiki/Antifragile_(book)"),
]

BY_ID = {sid: (i + 1, text, url) for i, (sid, text, url) in enumerate(SOURCES)}


def cite(*ids, root="/"):
    out = []
    for sid in ids:
        n, _text, _url = BY_ID[sid]
        out.append(f'<a href="{root}sources/#{sid}">{n}</a>')
    return f'<sup class="src">{"".join(out)}</sup>'


def render_list(root="/"):
    rows = []
    for sid, text, url in SOURCES:
        n = BY_ID[sid][0]
        link = f' <a href="{html.escape(url)}" rel="noopener" target="_blank">↗</a>' if url else ""
        rows.append(f'<li id="{sid}" value="{n}">{html.escape(text)}{link}</li>')
    return '<ol class="srclist">' + "".join(rows) + "</ol>"
