"""高斯-勒让德（Gauss–Legendre）求积：节点与权重都选得最优。

m 个节点可以精确积分 2m−1 次多项式，是代数精度最高的求积公式。
标准区间是 [−1, 1]，用线性变换搬到 [a, b]：

    x = (b−a)/2 · t + (a+b)/2,   ∫ₐᵇ f dx = (b−a)/2 · Σ Aᵢ f(xᵢ)

节点/权重由勒让德多项式的零点给出（numpy 的 leggauss 直接算）。

>>> round(gauss_rule(lambda x: 1.0, 0.0, 1.0, 1), 10)
1.0
>>> round(gauss_rule(lambda x: x ** 5, 0.0, 1.0, 3), 10)  # 2·3−1=5 次精确
0.1666666667
"""

from collections.abc import Callable

import numpy as np
from matplotlib.axes import Axes

Func = Callable[[float], float]


def nodes_weights(m: int) -> tuple[np.ndarray, np.ndarray]:
    """[−1, 1] 上的 m 个勒让德节点与权重。

    >>> t, w = nodes_weights(2)
    >>> [round(float(v), 6) for v in t]
    [-0.57735, 0.57735]
    >>> [round(float(v), 6) for v in w]
    [1.0, 1.0]
    """
    return np.polynomial.legendre.leggauss(m)


def mapped_nodes(a: float, b: float, m: int) -> np.ndarray:
    """把 [−1, 1] 的节点搬到 [a, b]。

    >>> [round(float(v), 6) for v in mapped_nodes(0.0, 1.0, 2)]
    [0.211325, 0.788675]
    """
    t, _ = nodes_weights(m)
    return (b - a) / 2.0 * t + (a + b) / 2.0


def gauss_rule(f: Func, a: float, b: float, m: int) -> float:
    """m 点高斯-勒让德求积。

    >>> round(gauss_rule(lambda x: x, 0.0, 1.0, 1), 10)
    0.5
    >>> round(gauss_rule(lambda x: x * x, 0.0, 1.0, 2), 10)
    0.3333333333
    """
    t, w = nodes_weights(m)
    xs = (b - a) / 2.0 * t + (a + b) / 2.0
    total: float = sum(float(wi) * f(float(xi))
                       for wi, xi in zip(w, xs))
    return (b - a) / 2.0 * total


def evaluations(m: int) -> int:
    """m 点高斯公式只需 m 次函数求值。

    >>> evaluations(3)
    3
    """
    return m


def weights_on(a: float, b: float, m: int) -> np.ndarray:
    """[a, b] 上实际使用的权重 (b−a)/2 · Aᵢ。

    >>> [round(float(v), 6) for v in weights_on(0.0, 1.0, 1)]
    [1.0]
    """
    _, w = nodes_weights(m)
    return (b - a) / 2.0 * w


def draw(ax: Axes, f: Func, a: float, b: float, m: int,
         color: str = "tab:brown") -> list[object]:
    """在每个高斯节点处画一条竖线到曲线，并在曲线上标点。"""
    xs = mapped_nodes(a, b, m)
    ys = [f(float(x)) for x in xs]
    artists: list[object] = []
    i: int
    for i, x in enumerate(xs):
        artists.append(ax.plot([float(x), float(x)], [0.0, ys[i]],
                               color=color, lw=0.9, alpha=0.6, zorder=2)[0])
    points, = ax.plot([float(x) for x in xs], ys, linestyle="none",
                      marker="o", markersize=5, color=color, zorder=3)
    artists.append(points)
    return artists
