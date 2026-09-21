"""使用 Matplotlib 绘制圆形。"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle

from image_utils import save_figure


SCREEN_WIDTH = 700
SCREEN_HEIGHT = 600
FIGURE_DPI = 100


def draw_circle(radius: float = 120, *, show: bool = True) -> Path:
    """绘制并保存圆形，可选择是否显示 Matplotlib 窗口。"""
    if radius <= 0:
        raise ValueError("radius 必须大于 0")

    figure, axes = plt.subplots(
        figsize=(SCREEN_WIDTH / FIGURE_DPI, SCREEN_HEIGHT / FIGURE_DPI),
        dpi=FIGURE_DPI,
    )
    figure.canvas.manager.set_window_title("Circle")
    figure.subplots_adjust(left=0, right=1, bottom=0, top=1)

    axes.add_patch(
        Circle(
            (0, 0),
            radius,
            fill=False,
            edgecolor="blue",
            linewidth=2,
        )
    )
    axes.set_xlim(-SCREEN_WIDTH / 2, SCREEN_WIDTH / 2)
    axes.set_ylim(-SCREEN_HEIGHT / 2, SCREEN_HEIGHT / 2)
    axes.set_aspect("equal", adjustable="box")
    axes.axis("off")

    saved_path = save_figure(figure, "circle.png")
    print(f"Saved image: {saved_path}")

    if show:
        plt.show()
    else:
        plt.close(figure)

    return saved_path


if __name__ == "__main__":
    draw_circle()
