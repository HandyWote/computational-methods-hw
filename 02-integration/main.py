"""编排：画板 → 坐标轴 → 原始函数 → 下拉选方法 → 方法参数 → 图形。

运行：uv run main.py  → 弹出 matplotlib 窗口。

交互流程：
    1. 进来只显示原函数；
    2. 下拉栏选积分方法（矩形 / 梯形 / 辛普森 / 龙贝格 / 高斯）；
    3. 选中后出现该方法自己的参数：
         矩形法   → 左/中/右按钮 + 拆分度 n
         梯形法   → 拆分度 n
         辛普森法 → 拆分度 n（自动保证偶数）
         龙贝格法 → 二分次数 k
         高斯法   → 节点数 m
    4. 图下实时显示近似值、真值与误差。
"""

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.widgets import Button, Slider

import axes
import dropdown
import function
import gauss
import rectangle
import romberg
import simpson
import trapezoid

matplotlib.rcParams["font.sans-serif"] = ["PingFang SC"]  # 中文
matplotlib.rcParams["axes.unicode_minus"] = False

METHODS: list[str] = ["矩形法", "梯形法", "辛普森法", "龙贝格法", "高斯法"]
KINDS: list[tuple[str, str]] = [
    ("left", "左矩形"),
    ("mid", "中矩形"),
    ("right", "右矩形"),
]

UI: dict[str, object] = {}  # 控件引用（调试/测试用）


def main() -> None:
    fig = plt.figure(figsize=(10, 8))            # 画板
    ax = fig.add_axes([0.07, 0.22, 0.86, 0.70])  # 主图
    axes.draw_axes(ax)                            # 坐标系
    function.draw_function(ax)                    # 原始函数曲线

    state: dict[str, object] = {"method": None, "kind": "mid",
                                "n": 8, "k": 3, "m": 3, "artists": []}

    info = fig.text(0.07, 0.145, "", fontsize=11)  # 图下信息栏

    def clear() -> None:
        """移除上一次画的近似图形。"""
        artist: object
        for artist in state["artists"]:  # type: ignore[union-attr]
            artist.remove()  # type: ignore[attr-defined]
        state["artists"] = []

    def apply(method: str) -> tuple[float, int, str]:
        """画当前方法的近似图形，返回 (近似值, 求值次数, 参数说明)。"""
        kind: str = str(state["kind"])
        if method == "矩形法":
            n: int = int(state["n"])
            state["artists"] = rectangle.draw(ax, function.f, function.A,
                                              function.B, n, kind)
            return (rectangle.rectangle_rule(function.f, function.A,
                                             function.B, n, kind),
                    n, f"n={n}  {dict(KINDS)[kind]}")
        if method == "梯形法":
            n = int(state["n"])
            state["artists"] = trapezoid.draw(ax, function.f, function.A,
                                              function.B, n)
            return (trapezoid.trapezoid_rule(function.f, function.A,
                                             function.B, n),
                    trapezoid.evaluations(n), f"n={n}")
        if method == "辛普森法":
            n = int(state["n"])
            state["artists"] = simpson.draw(ax, function.f, function.A,
                                            function.B, n)
            return (simpson.simpson_rule(function.f, function.A,
                                         function.B, n),
                    simpson.evaluations(n), f"n={n}")
        if method == "龙贝格法":
            k: int = int(state["k"])
            state["artists"] = romberg.draw(ax, function.f, function.A,
                                            function.B, k)
            return (romberg.romberg_rule(function.f, function.A,
                                         function.B, k),
                    romberg.evaluations(k), f"k={k}（{2 ** k} 段梯形）")
        m: int = int(state["m"])
        state["artists"] = gauss.draw(ax, function.f, function.A,
                                      function.B, m)
        return (gauss.gauss_rule(function.f, function.A, function.B, m),
                gauss.evaluations(m), f"m={m}")

    def update_params() -> None:
        """只显示当前方法需要的参数控件。"""
        method = state["method"]
        shown: dict[str, str] = {
            "矩形法": "n", "梯形法": "n", "辛普森法": "n",
            "龙贝格法": "k", "高斯法": "m",
        }
        need: str | None = shown.get(str(method)) if method else None
        name: str
        for name in ("n", "k", "m"):
            slider: Slider = UI[f"slider_{name}"]  # type: ignore[assignment]
            on: bool = name == need
            # 只让当前滑块可见且可交互：matplotlib 的 Slider 用
            # ax.contains(event) 判断命中，不看可见性，
            # 三个滑块叠在同位置时必须同时关掉 active，否则会抢鼠标。
            slider.ax.set_visible(on)
            slider.active = on
        i: int
        for i in range(len(KINDS)):
            UI[f"kind_ax_{i}"].set_visible(method == "矩形法")  # type: ignore[union-attr]

    def redraw() -> None:
        """重画近似图形并刷新信息栏。"""
        clear()
        method = state["method"]
        if method is None:
            info.set_text("")
            fig.canvas.draw_idle()
            return
        value, evals, params = apply(str(method))
        err: float = abs(value - function.EXACT)
        info.set_text(
            f"{method}  {params}  近似值={value:.12f}  "
            f"真值={function.EXACT:.12f}  误差={err:.3e}  求值={evals} 次")
        fig.canvas.draw_idle()

    # ---- 下拉栏：选择积分方法 ----
    def on_method(name: str) -> None:
        state["method"] = name
        # 辛普森法只接受偶数段：直接改滑块档位（2,4,6,…），从源头保证
        if name == "辛普森法":
            set_range("n", 2.0, 64.0, 2.0)
        else:
            set_range("n", 1.0, 64.0, 1.0)
        update_params()
        redraw()

    UI["dropdown"] = dropdown.Dropdown(
        fig, [0.07, 0.055, 0.19, 0.045], METHODS, on_method)

    # ---- 方法参数：矩形法的"左/中/右"按钮 ----
    kind_buttons: list[Button] = []
    k: int
    for k, (kind, label) in enumerate(KINDS):
        pos = [0.29 + k * 0.095, 0.055, 0.09, 0.045]
        kind_ax: Axes = fig.add_axes(pos)
        UI[f"kind_ax_{k}"] = kind_ax
        button: Button = Button(kind_ax, label)
        button.label.set_fontsize(9)

        def on_kind(_event, kind: str = kind) -> None:
            state["kind"] = kind
            highlight()
            redraw()

        button.on_clicked(on_kind)
        kind_buttons.append(button)

    def highlight() -> None:
        """当前"选取点"对应按钮涂橙色。"""
        i: int
        for i, (kind, _) in enumerate(KINDS):
            on: bool = kind == state["kind"]
            kind_buttons[i].color = "tab:orange" if on else "0.88"
            kind_buttons[i].hovercolor = "tab:orange" if on else "0.78"
            kind_buttons[i].ax.set_facecolor(kind_buttons[i].color)
        fig.canvas.draw_idle()

    # ---- 三个滑块，同一位置，按方法切换显示 ----
    def set_range(key: str, vmin: float, vmax: float, step: float) -> None:
        """改滑块档位（同步坐标轴范围并重新对齐当前值）；不触发回调。"""
        slider: Slider = UI[f"slider_{key}"]  # type: ignore[assignment]
        eventson: bool = slider.eventson
        slider.eventson = False
        slider.valmin = vmin
        slider.valmax = vmax
        slider.valstep = step
        slider.ax.set_xlim(vmin, vmax)
        value: float = min(vmax, max(vmin, float(state[key])))
        value = vmin + round((value - vmin) / step) * step
        slider.set_val(value)
        slider.eventson = eventson
        state[key] = int(round(value))

    def make_slider(key: str, label: str, vmin: float, vmax: float,
                    valinit: int) -> Slider:
        slider_ax = fig.add_axes([0.69, 0.062, 0.24, 0.03])
        UI[f"slider_{key}_ax"] = slider_ax
        slider: Slider = Slider(slider_ax, label, vmin, vmax,
                                valinit=valinit, valstep=1)
        slider.label.set_fontsize(10)

        def on_slide(value: float, key: str = key) -> None:
            state[key] = int(round(value))
            redraw()

        slider.on_changed(on_slide)
        return slider

    UI["slider_n"] = make_slider("n", "拆分度 n", 1, 64, int(state["n"]))
    UI["slider_k"] = make_slider("k", "二分次数 k", 0, 8, int(state["k"]))
    UI["slider_m"] = make_slider("m", "节点数 m", 1, 6, int(state["m"]))

    highlight()
    update_params()
    redraw()
    plt.show()


if __name__ == "__main__":
    main()
