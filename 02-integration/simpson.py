"""辛普森（抛物线）积分法：过三点作抛物线代替曲线。

复化辛普森把 [a, b] 分成 n 段（调用方保证 n 为偶数，每两段共用一条抛物线）：

    Sₙ = h/3 · [f₀ + 4(f₁+f₃+…) + 2(f₂+f₄+…) + fₙ],  h=(b−a)/n

误差 O(h⁴)，同样段数下比梯形准得多。

>>> round(simpson_rule(lambda x: x ** 3, 0.0, 1.0, 2), 10)
0.25
>>> round(simpson_rule(lambda x: x ** 3, 0.0, 1.0, 4), 10)
0.25
"""

from collections.abc import Callable

import numpy as np
from matplotlib.axes import Axes

Func = Callable[[float], float]


def simpson_rule(f: Func, a: float, b: float, n: int) -> float:
    """复化辛普森公式（n 为偶数，由调用方保证）。

    >>> simpson_rule(lambda x: 1.0, 0.0, 1.0, 2)
    1.0
    >>> simpson_rule(lambda x: x, 0.0, 1.0, 4)
    0.5
    """
    h: float = (b - a) / n
    total: float = f(a) + f(b)
    k: int
    for k in range(1, n):
        total += (4.0 if k % 2 else 2.0) * f(a + k * h)
    return total * h / 3.0


def evaluations(n: int) -> int:
    """复化辛普森在 n 段时共需 n+1 次函数求值。

    >>> evaluations(8)
    9
    """
    return n + 1


def draw(ax: Axes, f: Func, a: float, b: float, n: int,
         color: str = "tab:red", samples: int = 12) -> list[object]:
    """每两段画一段过三点的抛物线，返回 artist 列表。"""
    h: float = (b - a) / n
    artists: list[object] = []
    j: int
    for j in range(0, n, 2):
        x0: float = a + j * h
        x1: float = x0 + h
        x2: float = x0 + 2 * h
        coeff = np.polyfit([x0, x1, x2], [f(x0), f(x1), f(x2)], 2)
        xs = np.linspace(x0, x2, samples + 1)
        ys = np.polyval(coeff, xs)
        artists.append(ax.fill_between(xs, ys, 0.0, color=color,
                                       alpha=0.35, lw=0, zorder=2))
        artists.append(ax.plot(xs, ys, color=color, lw=0.9, zorder=2)[0])
    points, = ax.plot([a + k * h for k in range(n + 1)],
                      [f(a + k * h) for k in range(n + 1)],
                      linestyle="none", marker="o", markersize=3.5,
                      color=color, zorder=3)
    artists.append(points)
    return artists
