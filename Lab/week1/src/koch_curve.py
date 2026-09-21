"""使用 Matplotlib 和递归算法绘制 Koch 雪花。"""

import math
from pathlib import Path

import matplotlib.pyplot as plt

from image_utils import save_figure


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
FIGURE_DPI = 100

Point = tuple[float, float]


def _append_koch_points(
    points: list[Point],
    start: Point,
    heading: float, # 角度
    length: float,
    order: int,
) -> Point:
    """递归追加一段 Koch 曲线的顶点，并返回终点。"""
    if order == 0:
        angle = math.radians(heading)
        end = (
            start[0] + length * math.cos(angle),
            start[1] + length * math.sin(angle),
        )
        points.append(end)
        return end

    segment = length / 3
    point = start
    for turn in (0, 60, -120, 60):
        heading += turn
        point = _append_koch_points(
            points,
            point,
            heading,
            segment,
            order - 1,
        )
    return point


def koch_curve(
    length: float,
    order: int,
    *,
    start: Point = (0.0, 0.0),
    heading: float = 0.0,
) -> list[Point]:
    """计算一段 Koch 曲线的全部顶点。"""
    if length <= 0:
        raise ValueError("length 必须大于 0")
    if order < 0:
        raise ValueError("order 不能小于 0")

    points = [start]
    _append_koch_points(points, start, heading, length, order)
    return points


def koch_snowflake_points(order: int, length: float) -> list[Point]:
    """计算由三段 Koch 曲线组成的雪花顶点。"""
    if order < 0:
        raise ValueError("order 不能小于 0")
    if length <= 0:
        raise ValueError("length 必须大于 0")

    triangle_height = length * math.sqrt(3) / 2
    point = (-length / 2, triangle_height / 3)
    heading = 0.0
    points = [point]

    for _ in range(3):
        side = koch_curve(length, order, start=point, heading=heading)
        points.extend(side[1:])
        point = side[-1]
        heading -= 120

    return points


def draw_koch_snowflake(
    order: int = 4,
    length: float = 480,
    *,
    show: bool = True,
) -> Path:
    """绘制并保存 Koch 雪花，可选择是否显示 Matplotlib 窗口。"""
    points = koch_snowflake_points(order, length)
    x_coordinates, y_coordinates = zip(*points)

    figure, axes = plt.subplots(
        figsize=(SCREEN_WIDTH / FIGURE_DPI, SCREEN_HEIGHT / FIGURE_DPI),
        dpi=FIGURE_DPI,
    )
    figure.canvas.manager.set_window_title("Koch Snowflake")
    figure.subplots_adjust(left=0, right=1, bottom=0, top=1)

    axes.plot(x_coordinates, y_coordinates, color="purple", linewidth=2)
    axes.set_xlim(-SCREEN_WIDTH / 2, SCREEN_WIDTH / 2)
    axes.set_ylim(-SCREEN_HEIGHT / 2, SCREEN_HEIGHT / 2)
    axes.set_aspect("equal", adjustable="box")
    axes.axis("off")

    saved_path = save_figure(figure, "koch_curve.png")
    print(f"Saved image: {saved_path}")

    if show:
        plt.show()
    else:
        plt.close(figure)

    return saved_path


if __name__ == "__main__":
    draw_koch_snowflake()
