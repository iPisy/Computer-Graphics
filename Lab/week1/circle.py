import turtle

def draw_circle(radius: int = 120):
    # 创建画布
    screen = turtle.Screen()
    screen.title("circle")
    screen.setup(width=700, height=600)

    # 创建画笔
    pen = turtle.Turtle()
    pen.speed(0)
    pen.pensize(2)
    pen.color("blue")

    # 绘制圆形
    pen.circle(radius)
    pen.hideturtle()

    screen.mainloop()·


if __name__ == "__main__":
    draw_circle()
