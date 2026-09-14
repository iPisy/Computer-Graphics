"""使用 turtle 和递归算法绘制 Koch 雪花。"""

import math

import turtle
from PIL import ImageDraw

from image_utils import save_image


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700


# 绘制 Koch 曲线的函数。
def koch_curve(pen: turtle.Turtle, length: float, order: int) -> None:
    if order < 0:
        raise ValueError("order 不能小于 0")

    # 递归出口
    if order == 0:
        pen.forward(length)
        return

    # 将线段分为三等分，并递归绘制每一段。
    segment = length / 3
    koch_curve(pen, segment, order - 1)
    pen.left(60)
    koch_curve(pen, segment, order - 1)
    pen.right(120)
    koch_curve(pen, segment, order - 1)
    pen.left(60)
    koch_curve(pen, segment, order - 1)


def _to_image_coordinates(
    point: tuple[float, float],
) -> tuple[float, float]:
    """Convert turtle coordinates (y-up) to image coordinates (y-down)."""
    x, y = point
    return SCREEN_WIDTH / 2 + x, SCREEN_HEIGHT / 2 - y


def _draw_koch_image_segment(
    draw: ImageDraw.ImageDraw,
    start: tuple[float, float],
    heading: float,
    length: float,
    order: int,
) -> tuple[tuple[float, float], float]:
    """Draw one Koch segment into a PIL image and return its endpoint."""
    if order == 0:
        angle = math.radians(heading)
        end = (
            start[0] + length * math.cos(angle),
            start[1] + length * math.sin(angle),
        )
        draw.line(
            [_to_image_coordinates(start), _to_image_coordinates(end)],
            fill="purple",
            width=2,
        )
        return end, heading

    segment = length / 3
    point, heading = _draw_koch_image_segment(
        draw, start, heading, segment, order - 1
    )
    heading += 60
    point, heading = _draw_koch_image_segment(
        draw, point, heading, segment, order - 1
    )
    heading -= 120
    point, heading = _draw_koch_image_segment(
        draw, point, heading, segment, order - 1
    )
    heading += 60
    return _draw_koch_image_segment(draw, point, heading, segment, order - 1)


def _draw_koch_image(
    draw: ImageDraw.ImageDraw,
    order: int,
    length: float,
) -> None:
    """Draw the same Koch snowflake as the turtle window on a PIL canvas."""
    triangle_height = length * math.sqrt(3) / 2
    point = (-length / 2, triangle_height / 3)
    heading = 0.0

    for _ in range(3):
        point, heading = _draw_koch_image_segment(
            draw, point, heading, length, order
        )
        heading -= 120  # turtle.right(120)


# 绘制由三条 Koch 曲线组成的雪花
def draw_koch_snowflake(order: int = 4, length: float = 480) -> None:
    if order < 0:
        raise ValueError("order 不能小于 0")

    screen = turtle.Screen()
    screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    screen.title("Koch Snowflake")
    screen.bgcolor("white")
    screen.tracer(0)

    pen = turtle.Turtle()
    pen.hideturtle()
    pen.speed(0)
    pen.pensize(2)
    pen.pencolor("purple")

    # 从等边三角形的左上角开始，使整个雪花位于窗口中央。
    triangle_height = length * math.sqrt(3) / 2
    pen.penup()
    pen.goto(-length / 2, triangle_height / 3)
    pen.setheading(0)
    pen.pendown()

    # 顺时针绘制三条边，使每条 Koch 曲线的凸起都朝三角形外侧。
    for _ in range(3):
        koch_curve(pen, length, order)
        # 画完一条边，顺时针旋转120度，为绘制下一条边做准备。
        pen.right(120)

    screen.update()
    saved_path = save_image(
        filename="koch_curve.png",
        size=(SCREEN_WIDTH, SCREEN_HEIGHT),
        draw_image=lambda draw: _draw_koch_image(draw, order, length),
    )
    print(f"Saved image: {saved_path}")
    screen.mainloop()


if __name__ == "__main__":
    draw_koch_snowflake()
