"""龙贝格（Romberg）积分：复化梯形 + Richardson 外推。

先用二分递推算出梯形值序列 T₀, T₁, T₂, …（T_k 用 2^k 段），
再对相邻两行做外推，把误差里的 h² 项、h⁴ 项逐次消掉：

    R[k][0] = T_k
    R[k][j] = R[k][j−1] + (R[k][j−1] − R[k−1][j−1]) / (4^j − 1)

取对角元 R[k][k] 作为结果，精度可达 O(h^(2k+2))。

>>> round(romberg_rule(lambda x: x ** 3, 0.0, 1.0, 1), 10)
0.25
>>> round(romberg_rule(lambda x: x ** 3, 0.0, 1.0, 3), 10)
0.25
"""

from collections.abc import Callable

from matplotlib.axes import Axes

import trapezoid

Func = Callable[[float], float]


def trapezoid_levels(f: Func, a: float, b: float, kmax: int) -> list[float]:
    """T₀ … T_kmax，其中 T_k 是把区间二分 k 次（2^k 段）的复化梯形值。

    >>> [round(t, 6) for t in trapezoid_levels(lambda x: x, 0.0, 1.0, 2)]
    [0.5, 0.5, 0.5]
    """
    levels: list[float] = [(b - a) / 2.0 * (f(a) + f(b))]
    h: float = b - a
    k: int
    for k in range(1, kmax + 1):
        h /= 2.0
        mid: float = sum(f(a + (2 * i - 1) * h)
                         for i in range(1, 2 ** (k - 1) + 1))
        levels.append(levels[-1] / 2.0 + h * mid)
    return levels


def table(f: Func, a: float, b: float, kmax: int) -> list[list[float]]:
    """外推表 R（下三角），R[k][j] 为第 k 行第 j 次外推值。

    >>> [round(row[-1], 6) for row in table(lambda x: x ** 3, 0.0, 1.0, 2)]
    [0.5, 0.25, 0.25]
    """
    levels: list[float] = trapezoid_levels(f, a, b, kmax)
    rows: list[list[float]] = []
    k: int
    for k in range(kmax + 1):
        row: list[float] = [levels[k]]
        j: int
        for j in range(1, k + 1):
            row.append(row[j - 1]
                       + (row[j - 1] - rows[k - 1][j - 1]) / (4 ** j - 1))
        rows.append(row)
    return rows


def romberg_rule(f: Func, a: float, b: float, k: int) -> float:
    """二分 k 次并外推到第 k 层，返回 R[k][k]。

    >>> round(romberg_rule(lambda x: 1.0, 0.0, 2.0, 0), 10)
    2.0
    """
    return table(f, a, b, k)[k][k]


def evaluations(k: int) -> int:
    """二分 k 次的梯形序列共需 2^k + 1 次函数求值。

    >>> evaluations(3)
    9
    """
    return 2 ** k + 1


def draw(ax: Axes, f: Func, a: float, b: float, k: int,
         color: str = "tab:purple") -> list[object]:
    """画出二分 k 次后最细一层的梯形（2^k 段）。"""
    return trapezoid.draw(ax, f, a, b, 2 ** k, color=color)
