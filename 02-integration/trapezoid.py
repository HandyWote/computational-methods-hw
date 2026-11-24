"""梯形积分法：用弦（过两端点的一次插值）代替曲线。

复化梯形（n 等分，h=(b−a)/n）：

    Tₙ = h/2 · [f(a) + 2Σ_{k=1}^{n−1} f(a+kh) + f(b)]

>>> round(trapezoid_rule(lambda x: x * x, 0.0, 1.0, 1), 10)
0.5
>>> round(trapezoid_rule(lambda x: x * x, 0.0, 1.0, 10000), 6)
0.333333
"""

from collections.abc import Callable

from matplotlib.axes import Axes
from matplotlib.patches import Polygon

Func = Callable[[float], float]


def trapezoid_rule(f: Func, a: float, b: float, n: int) -> float:
    """复化梯形公式。

    >>> trapezoid_rule(lambda x: 1.0, 0.0, 2.0, 5)
    2.0
    >>> round(trapezoid_rule(lambda x: x, 0.0, 1.0, 3), 10)
    0.5
    """
    if n < 1:
        raise ValueError("n 必须是正整数")
    h: float = (b - a) / n
    total: float = f(a) + f(b)
    k: int
    for k in range(1, n):
        total += 2.0 * f(a + k * h)
    return total * h / 2.0


def pieces(f: Func, a: float, b: float,
           n: int) -> list[tuple[float, float, float, float]]:
    """每段梯形的 [(左端, 左高, 右端, 右高), ...]，计算与画图共用。

    >>> pieces(lambda x: x, 0.0, 1.0, 2)
    [(0.0, 0.0, 0.5, 0.5), (0.5, 0.5, 1.0, 1.0)]
    """
    if n < 1:
        raise ValueError("n 必须是正整数")
    h: float = (b - a) / n
    return [(a + k * h, f(a + k * h), a + (k + 1) * h, f(a + (k + 1) * h))
            for k in range(n)]


def evaluations(n: int) -> int:
    """复化梯形共需 n+1 次函数求值。

    >>> evaluations(8)
    9
    """
    return n + 1


def draw(ax: Axes, f: Func, a: float, b: float, n: int,
         color: str = "tab:green") -> list[object]:
    """在画板上画出 n 个梯形，返回 artist 列表（重绘前逐个 remove）。"""
    artists: list[object] = []
    left: float
    left_y: float
    right: float
    right_y: float
    for left, left_y, right, right_y in pieces(f, a, b, n):
        artists.append(ax.add_patch(Polygon(
            [(left, 0.0), (left, left_y), (right, right_y), (right, 0.0)],
            closed=True, facecolor=color, alpha=0.35,
            edgecolor=color, lw=0.9, zorder=2)))
    points, = ax.plot([a + (b - a) * k / n for k in range(n + 1)],
                      [f(a + (b - a) * k / n) for k in range(n + 1)],
                      linestyle="none", marker="o", markersize=3.5,
                      color=color, zorder=3)
    artists.append(points)
    return artists
