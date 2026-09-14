"""使用 turtle 绘制一个圆。"""

import turtle


def draw_circle(radius: int = 120) -> None:
    """绘制指定半径的圆。"""
    screen = turtle.Screen()
    screen.title("圆")
    screen.setup(width=700, height=600)

    pen = turtle.Turtle()
    pen.speed(0)
    pen.pensize(2)
    pen.color("blue")

    # turtle.circle() 会以当前位置为起点绘制指定半径的圆。
    pen.circle(radius)
    pen.hideturtle()

    screen.mainloop()


if __name__ == "__main__":
    draw_circle()
