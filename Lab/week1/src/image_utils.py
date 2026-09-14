"""Reusable helpers for rendering and saving PIL images."""

from collections.abc import Callable
from pathlib import Path

from PIL import Image, ImageDraw


DrawImage = Callable[[ImageDraw.ImageDraw], None]
DEFAULT_OUTPUT_DIRECTORY = Path(__file__).resolve().parent.parent / "docs" / "images"


def save_image(
    filename: str | Path,
    size: tuple[int, int],
    draw_image: DrawImage,
    *,
    output_directory: str | Path = DEFAULT_OUTPUT_DIRECTORY,
    background: str = "white",
    mode: str = "RGB",
) -> Path:
    """Draw and save an image under ``../docs/images`` by default.

    Pass another ``output_directory`` only when the image belongs elsewhere.
    ``filename`` must contain a file name only, keeping the two responsibilities
    separate and making call sites easy to read.
    """
    width, height = size
    if width <= 0 or height <= 0:
        raise ValueError("image width and height must be greater than 0")

    name = Path(filename)
    if not name.name or name != Path(name.name):
        raise ValueError("filename must not contain a path; use output_directory")

    path = Path(output_directory) / name
    path.parent.mkdir(parents=True, exist_ok=True)

    with Image.new(mode, size, background) as image:
        draw_image(ImageDraw.Draw(image))
        image.save(path)

    return path
