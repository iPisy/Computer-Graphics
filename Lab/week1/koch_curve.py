"""使用 turtle 和递归算法绘制 Koch 雪花。"""

import math
import turtle


def koch_curve(pen: turtle.Turtle, length: float, order: int) -> None:
    """从画笔当前位置开始，递归绘制一条 Koch 曲线。"""
    if order < 0:
        raise ValueError("order 不能小于 0")

    if order == 0:
        pen.forward(length)
        return

    segment = length / 3
    koch_curve(pen, segment, order - 1)
    pen.left(60)
    koch_curve(pen, segment, order - 1)
    pen.right(120)
    koch_curve(pen, segment, order - 1)
    pen.left(60)
    koch_curve(pen, segment, order - 1)


def draw_koch_snowflake(order: int = 4, length: float = 480) -> None:
    """绘制由三条 Koch 曲线组成的雪花。"""
    if order < 0:
        raise ValueError("order 不能小于 0")

    screen = turtle.Screen()
    screen.setup(width=800, height=700)
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
        pen.right(120)

    screen.update()
    screen.mainloop()


if __name__ == "__main__":
    draw_koch_snowflake()
