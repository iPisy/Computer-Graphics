"""用不同字体、颜色和字号在屏幕上显示“计算机图形学”。"""

from pathlib import Path

import matplotlib.pyplot as plt

from image_utils import save_figure


TEXT = "计算机图形学"
STYLES = (
    ("Microsoft YaHei", "#D64550", 28, 0.82),
    ("SimHei", "#168A79", 36, 0.60),
    ("SimSun", "#2864B4", 44, 0.38),
    ("KaiTi", "#804CB5", 52, 0.16),
)


def draw_text(*, show: bool = True) -> Path:
    """绘制四种文字效果，保存图像，并按需显示窗口。"""
    figure, axes = plt.subplots(figsize=(9, 7), dpi=120)
    figure.patch.set_facecolor("#F8F9FC")
    axes.set_facecolor("#F8F9FC")
    figure.subplots_adjust(left=0.05, right=0.95, top=0.96, bottom=0.04)
    axes.axis("off") # 隐藏坐标轴

    for font, color, size, y in STYLES:
        axes.text(
            0.08,
            y,
            TEXT,
            transform=axes.transAxes,
            fontfamily=font,
            fontsize=size,
            color=color,
            va="center",
        )

    saved_path = save_figure(figure, "text_styles.png")
    print(f"图像已保存：{saved_path}")

    if show:
        plt.show()
    plt.close(figure)
    return saved_path


if __name__ == "__main__":
    draw_text()
