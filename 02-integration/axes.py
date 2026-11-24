"""坐标数轴：完整 x/y 轴，原点在中心，带箭头、主次刻度、轴名。

只负责在给定的 Axes 上画坐标系，不创建画板。

刻度分两级：主刻度带数字，5 个次刻度细分成一格，
例如 [-2, 2] 上主刻度 0.5、次刻度 0.1。

样例：fig, ax = plt.subplots(); draw_axes(ax) 得到 [-1.5, 1.5] 的坐标系。
"""

import math

from matplotlib.axes import Axes

LIMIT: float = 1.5          # 坐标范围 [-LIMIT, LIMIT]
MAJOR_STEP: float = 0.5  # 主刻度间距（带数字）
MINOR_DIV: int = 5       # 每个主刻度内再分几格（次刻度）


def tick_values(limit: float, step: float) -> list[float]:
    """生成 (-limit, limit) 内步长为 step 的刻度值（两端留半格，避开箭头）。

    >>> tick_values(2.0, 0.5)
    [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]
    >>> tick_values(1.0, 0.5)
    [-0.5, 0.0, 0.5]
    """
    last: int = math.floor((limit - step / 2) / step + 1e-9)
    return [round(k * step, 10) for k in range(-last, last + 1)]


def format_tick(value: float, step: float) -> str:
    """按刻度间距决定小数位数，并去掉多余的尾随 0。

    >>> format_tick(0.5, 0.5)
    '0.5'
    >>> format_tick(1.0, 0.5)
    '1'
    >>> format_tick(0.0, 0.5)
    '0'
    """
    decimals: int = 0
    while abs(round(step, decimals) - step) > 1e-9:
        decimals += 1
    text: str = f"{value:.{decimals}f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


def draw_axes(ax: Axes, limit: float = LIMIT,
              major_step: float = MAJOR_STEP,
              minor_div: int = MINOR_DIV) -> Axes:
    """在画板上画穿过原点的完整 x/y 数轴。

    :param ax: 画板
    :param limit: 坐标范围 [-limit, limit]
    :param major_step: 主刻度（带数字）的间距
    :param minor_div: 每个主刻度等分成几格次刻度
    :return: 画板（链式调用用）
    """
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_aspect("equal")
    ax.axis("off")  # 关掉默认边框，手工画数轴

    # ---- x 轴 / y 轴（穿过原点）----
    ax.plot([-limit, limit], [0.0, 0.0], color="black", lw=1.2, zorder=1)
    ax.plot([0.0, 0.0], [-limit, limit], color="black", lw=1.2, zorder=1)

    # 轴末端箭头
    arrow_kw: dict[str, object] = {"color": "black", "lw": 0}
    ax.annotate("", xy=(limit, 0.0), xytext=(limit - limit * 0.06, 0.0),
                arrowprops={**arrow_kw, "arrowstyle": "-|>",
                            "mutation_scale": 14})
    ax.annotate("", xy=(0.0, limit), xytext=(0.0, limit - limit * 0.06),
                arrowprops={**arrow_kw, "arrowstyle": "-|>",
                            "mutation_scale": 14})

    # ---- 刻度：先次刻度，再主刻度（主刻度更长、带数字）----
    tick_half: float = limit * 0.018       # 主刻度线半长
    minor_half: float = tick_half * 0.55   # 次刻度线半长
    label_off: float = limit * 0.06        # 数字离轴的距离
    minor_step: float = major_step / minor_div

    v: float
    for v in tick_values(limit, minor_step):
        if abs(v / major_step - round(v / major_step)) < 1e-9:
            continue  # 主刻度位置留给下面画
        ax.plot([v, v], [-minor_half, minor_half], color="black", lw=0.8, zorder=2)
        ax.plot([-minor_half, minor_half], [v, v], color="black", lw=0.8, zorder=2)

    for v in tick_values(limit, major_step):
        if abs(v) > 1e-12:
            # x 轴刻度（原点单独标，跳过）
            ax.plot([v, v], [-tick_half, tick_half], color="black", lw=1, zorder=2)
            ax.text(v, -label_off, format_tick(v, major_step),
                    ha="center", va="top", fontsize=9)
            # y 轴刻度
            ax.plot([-tick_half, tick_half], [v, v], color="black", lw=1, zorder=2)
            ax.text(-label_off, v, format_tick(v, major_step),
                    ha="right", va="center", fontsize=9)

    # 原点与轴名
    ax.text(-label_off, -label_off, "0", ha="right", va="top", fontsize=9)
    ax.text(limit + limit * 0.03, 0.0, "x", ha="left", va="center",
            fontsize=12, style="italic")
    ax.text(0.0, limit + limit * 0.03, "y", ha="center", va="bottom",
            fontsize=12, style="italic")

    return ax
