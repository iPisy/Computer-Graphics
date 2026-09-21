# 将指定图片保存至指定位置，含默认目录。

from pathlib import Path

from matplotlib.figure import Figure


DEFAULT_OUTPUT_DIRECTORY = Path(__file__).resolve().parent.parent / "docs" / "images"


def save_figure(
    figure: Figure,
    filename: str | Path,
    *,
    output_directory: str | Path = DEFAULT_OUTPUT_DIRECTORY,
) -> Path:
    
    name = Path(filename)
    if not name.name or name != Path(name.name):
        raise ValueError("filename 不能包含路径，请使用 output_directory")

    path = Path(output_directory) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(
        path,
        dpi=figure.dpi,
        facecolor=figure.get_facecolor(),
        edgecolor="none",
    )
    return path
