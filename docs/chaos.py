#!/usr/bin/env python3
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
