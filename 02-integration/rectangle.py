"""矩形积分法（左 / 中 / 右矩形）及其图形展示。

用每段小区间上一个"选取点"的函数值作高度，乘区间宽度近似面积：

    左矩形  高度取左端点 f(x_k)
    中矩形  高度取中点   f(x_k + h/2)
    右矩形  高度取右端点 f(x_{k+1})

复化形式把 [a, b] 分成 n 段，h = (b−a)/n。

>>> round(rectangle_rule(lambda x: x * x, 0.0, 1.0, 1), 10)
0.25
>>> round(rectangle_rule(lambda x: x, 0.0, 1.0, 1, "left"), 10)
0.0
"""

from collections.abc import Callable

from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

Func = Callable[[float], float]


def sample_x(k: int, a: float, h: float, kind: str) -> float:
    """第 k 段的选取点位置。

    >>> [round(sample_x(0, 0.0, 0.5, k), 3) for k in ("left", "mid", "right")]
    [0.0, 0.25, 0.5]
    """
    if kind == "left":
        return a + k * h
    if kind == "right":
        return a + (k + 1) * h
    return a + (k + 0.5) * h


def pieces(f: Func, a: float, b: float, n: int,
           kind: str = "mid") -> list[tuple[float, float, float]]:
    """每段矩形的 [(左端, 宽, 高), ...]，供计算与画图共用。

    >>> pieces(lambda x: x, 0.0, 1.0, 2)
    [(0.0, 0.5, 0.25), (0.5, 0.5, 0.75)]
    >>> pieces(lambda x: x, 0.0, 1.0, 2, "left")
    [(0.0, 0.5, 0.0), (0.5, 0.5, 0.5)]
    """
    if n < 1:
        raise ValueError("n 必须是正整数")
    h: float = (b - a) / n
    return [(a + k * h, h, f(sample_x(k, a, h, kind))) for k in range(n)]


def rectangle_rule(f: Func, a: float, b: float, n: int,
                   kind: str = "mid") -> float:
    """复化矩形公式的积分近似值。

    >>> round(rectangle_rule(lambda x: 1.0, 0.0, 2.0, 4), 10)
    2.0
    >>> round(rectangle_rule(lambda x: 2 * x, 0.0, 1.0, 100, "right"), 4)
    1.01
    """
    return sum(width * height for _, width, height in pieces(f, a, b, n, kind))


def draw(ax: Axes, f: Func, a: float, b: float, n: int,
         kind: str = "mid", color: str = "tab:orange") -> list[object]:
    """在画板上画出 n 个矩形与它们的选取点。

    :return: 本次画出的 artist 列表（重绘前逐个 remove 即可）
    """
    artists: list[object] = []
    h: float = (b - a) / n
    left: float
    width: float
    height: float
    for left, width, height in pieces(f, a, b, n, kind):
        artists.append(ax.add_patch(
            Rectangle((left, 0.0), width, height,
                      facecolor=color, alpha=0.35,
                      edgecolor=color, lw=0.9, zorder=2)))
    xs: list[float] = [sample_x(k, a, h, kind) for k in range(n)] + [b]
    xs = [x for x in xs if x <= b]
    points, = ax.plot(xs, [f(x) for x in xs], linestyle="none",
                      marker="o", markersize=3.5, color=color, zorder=3)
    artists.append(points)
    return artists
