"""下拉选择栏：matplotlib 没有原生下拉框，这里用按钮 + 展开列表实现。

点击按钮展开选项列表，点某一项即选中并收起，然后回调 on_select。

样例：
    dd = Dropdown(fig, [0.07, 0.05, 0.17, 0.045], ["矩形法", "梯形法"],
                  on_select=lambda name: print(name))
"""

from collections.abc import Callable

from matplotlib.figure import Figure
from matplotlib.widgets import Button


class Dropdown:
    """按钮式下拉栏：value 为当前选项，None 表示未选择（显示占位文字）。"""

    def __init__(self, fig: Figure, rect: list[float], options: list[str],
                 on_select: Callable[[str], None],
                 placeholder: str = "选择积分方法",
                 direction: str = "up") -> None:
        self.fig: Figure = fig
        self.rect: list[float] = rect
        self.options: list[str] = list(options)
        self.on_select: Callable[[str], None] = on_select
        self.placeholder: str = placeholder
        self.direction: str = direction  # 列表展开方向："up" 或 "down"
        self.value: str | None = None
        self._list_ax = None
        self._buttons: list[Button] = []

        self.button_ax = fig.add_axes(rect, zorder=6)
        self.button: Button = Button(self.button_ax, self._label(),
                                     color="0.90", hovercolor="0.80")
        self.button.label.set_fontsize(10)
        self.button.on_clicked(self._toggle)

    # ---- 内部 ----

    def _label(self) -> str:
        """按钮上显示的文字（未选择时显示占位符）。

        >>> dd = Dropdown.__new__(Dropdown); dd.value = None; dd.placeholder = "选择积分方法"
        >>> dd._label()
        '选择积分方法  ▼'
        """
        return f"{self.value if self.value else self.placeholder}  ▼"

    def _toggle(self, _event) -> None:
        """点按钮：已展开则收起，否则展开。"""
        if self._list_ax is None:
            self.open()
        else:
            self.close()

    # ---- 对外 ----

    def open(self) -> None:
        """展开选项列表（默认向上展开，避免超出画布底部）。"""
        x, y, w, h = self.rect
        count: int = len(self.options)
        bottom: float = y + h if self.direction == "up" else y - count * h
        self._list_ax = self.fig.add_axes([x, bottom, w, count * h],
                                          zorder=7)
        self._list_ax.set_xticks([])
        self._list_ax.set_yticks([])
        self._list_ax.set_facecolor("white")
        self._list_ax.set_frame_on(True)
        self._buttons = []
        i: int
        for i, option in enumerate(self.options):
            if self.direction == "up":
                row_rect = [0.0, (count - 1 - i) / count, 1.0, 1.0 / count]
            else:
                row_rect = [0.0, 1.0 - (i + 1) / count, 1.0, 1.0 / count]
            row_ax = self._list_ax.inset_axes(row_rect)
            row: Button = Button(row_ax, option, color="white",
                                 hovercolor="0.90")
            row.label.set_fontsize(10)
            row.on_clicked(lambda _e, name=option: self.select(name))
            self._buttons.append(row)
        self.fig.canvas.draw_idle()

    def close(self) -> None:
        """收起选项列表。"""
        if self._list_ax is not None:
            self.fig.delaxes(self._list_ax)
            self._list_ax = None
            self._buttons = []
            self.fig.canvas.draw_idle()

    def select(self, option: str) -> None:
        """选中某一项：收起列表、更新按钮文字、触发 on_select 回调。"""
        self.value = option
        self.close()
        self.button.label.set_text(self._label())
        self.on_select(option)
