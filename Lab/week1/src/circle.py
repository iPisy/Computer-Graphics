import turtle
from PIL import ImageDraw

from image_utils import save_image


SCREEN_WIDTH = 700
SCREEN_HEIGHT = 600


def _draw_circle_image(draw: ImageDraw.ImageDraw, radius: int) -> None:
    """Draw the same circle as the turtle window on a PIL canvas."""
    # turtle.circle(radius) starts at the bottom of a circle whose center is
    # one radius above the turtle's starting point.
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    bounding_box = (
        center_x - radius,
        center_y - 2 * radius,
        center_x + radius,
        center_y,
    )
    draw.ellipse(bounding_box, outline="blue", width=2)


def draw_circle(radius: int = 120) -> None:
    # 创建画布
    screen = turtle.Screen()
    screen.title("circle")
    screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)

    # 创建画笔
    pen = turtle.Turtle()
    pen.speed(0)
    pen.pensize(2)
    pen.color("blue")

    # 绘制圆形
    pen.circle(radius)
    pen.hideturtle()

    screen.update()
    saved_path = save_image(
        filename="circle.png",
        size=(SCREEN_WIDTH, SCREEN_HEIGHT),
        draw_image=lambda draw: _draw_circle_image(draw, radius),
    )
    print(f"Saved image: {saved_path}")
    screen.mainloop()


if __name__ == "__main__":
    draw_circle()
