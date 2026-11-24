"""原始目标函数：f(x) = sin x / x，积分区间 [0, 1]。

课程第 4 章的贯穿例题（PPT 4-2 §40、4-3 §10、4-4 §17、4-5 §28）：

    I = ∫₀¹ sin x / x dx = 0.9460831…

f 在 x=0 处有可去奇点，按 lim_{x→0} f(x) = 1 补充定义 f(0)=1。

>>> f(0.0)
1.0
>>> round(f(1.0), 7)
0.841471
"""

import decimal
import fractions
import math

from matplotlib.axes import Axes

A: float = 0.0   # 积分下限
B: float = 1.0   # 积分上限

# 原函数的图例条目
LEGEND: str = "f(x) = sin x / x"


def f(x: float) -> float:
    """被积函数；x=0 处取极限值 1。

    >>> f(0.0)
    1.0
    >>> round(f(0.5), 7)
    0.9588511
    """
    if x == 0.0:
        return 1.0
    return math.sin(x) / x


def si1(terms: int = 12) -> float:
    """Si(1) 的幂级数：Σ_{k≥0} (−1)^k / ((2k+1)·(2k+1)!)，作为积分真值。

    >>> round(si1(), 13)
    0.9460830703672
    >>> abs(si1(8) - si1(14)) < 1e-15
    True
    """
    total: float = 0.0
    k: int
    for k in range(terms):
        total += (-1.0) ** k / ((2 * k + 1) * math.factorial(2 * k + 1))
    return total


EXACT: float = si1()  # 积分真值 ∫₀¹ sin x / x dx（双精度下精确）


def si1_digits(digits: int = 30) -> str:
    """用精确有理数级数 + Decimal 算出任意位的 Si(1)（不依赖第三方库）。

    级数 Σ(−1)^k/((2k+1)(2k+1)!) 的项以阶乘速度衰减，
    取 60 项在 60 位精度下已远超所需。

    >>> si1_digits(20)
    '0.94608307036718301494'
    >>> si1_digits(5)
    '0.94608'
    """
    context = decimal.getcontext()
    context.prec = digits + 20
    total = fractions.Fraction(0)
    k: int
    for k in range(60):
        total += fractions.Fraction((-1) ** k,
                                    (2 * k + 1) * math.factorial(2 * k + 1))
    value = decimal.Decimal(total.numerator) / decimal.Decimal(total.denominator)
    return f"{value:.{digits}f}"


def draw_function(ax: Axes, x_min: float = A, x_max: float = B,
                  samples: int = 400) -> Axes:
    """在画板上画原始函数曲线。

    样例：draw_function(ax) 在 [0, 1] 上画 401 个采样点的实线。

    :param ax: 画板
    :param x_min: 定义域左端
    :param x_max: 定义域右端
    :param samples: 采样点数
    :return: 画板（链式调用用）
    """
    xs: list[float] = [x_min + (x_max - x_min) * i / samples
                       for i in range(samples + 1)]
    ax.plot(xs, [f(x) for x in xs], color="tab:blue", lw=2.0,
            label=LEGEND, zorder=4)
    return ax
