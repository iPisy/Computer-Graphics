"""按作业上交规范导出 Lab，仅使用 Python 标准库（Python 3.10+）。"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile


EXPORT_DIRECTORY = Path(__file__).resolve().parent
LAB_DIRECTORY = EXPORT_DIRECTORY.parent
# 按十进制 MB 检查，确保严格小于规范中的 10M。
CODE_ZIP_LIMIT = 10_000_000
REPORT_NAME = re.compile(
    r"(?P<student_id>\d+)-(?P<name>.+?)-week_(?P<week>\d+)(?:[-_].+)?",
    re.IGNORECASE,
)
CODE_EXTENSIONS = set(
    ".py .pyi .pyx .pxd .c .cc .cpp .cxx .h .hpp .hxx .cs .java "
    ".js .jsx .ts .tsx .rs .go .m .mm .cu .cuh .cl "
    ".glsl .vert .frag .geom .tesc .tese .comp .hlsl .wgsl "
    ".sh .bat .cmd .ps1".split()
)
BUILD_FILES = {
    "requirements.txt", "pyproject.toml", "setup.cfg",
    "cmakelists.txt", "makefile", "cargo.toml", "package.json",
}
RESULT_EXTENSIONS = set(
    ".png .jpg .jpeg .bmp .gif .tif .tiff .webp .svg .apng "
    ".ppm .pgm .pbm .hdr .exr .mp4 .avi .mov .mkv .webm .wmv .m4v".split()
)
EXCLUDED_DIRECTORIES = {
    "__pycache__", "venv", "env", "node_modules", "build", "dist", "exports",
}


class ExportError(ValueError):
    """可由用户修正的输入或提交材料问题。"""


@dataclass
class ExportPlan:
    lab: Path
    report: Path
    pdfs: list[Path]
    stem: str
    output: Path
    code: list[Path]
    results: list[Path]
    skipped_code: list[Path]


def is_link(path: Path) -> bool:
    # Windows junction 也不应把 Lab 以外的目录引入压缩包。
    return path.is_symlink() or bool(
        getattr(path.lstat(), "st_file_attributes", 0) & 0x400
    )


def walk_files(
    directory: Path, excluded: set[str] | None = None, *, include_hidden: bool = False,
) -> list[Path]:
    if not directory.is_dir() or is_link(directory):
        return []
    found = []
    excluded = EXCLUDED_DIRECTORIES if excluded is None else excluded
    for root, directories, filenames in os.walk(directory):
        directories[:] = sorted(
            name for name in directories
            if (include_hidden or not name.startswith(".")) and name.lower() not in excluded
            and not is_link(Path(root) / name)
        )
        for name in sorted(filenames):
            path = Path(root) / name
            if (include_hidden or not name.startswith(".")) and path.is_file() and not is_link(path):
                found.append(path)
    return sorted(found)


def is_code(path: Path) -> bool:
    return path.suffix.lower() in CODE_EXTENSIONS or path.name.lower() in BUILD_FILES


def filename_part(value: str, label: str) -> str:
    if (
        not value or value in {".", ".."} or value.endswith((" ", "."))
        or re.search(r'[<>:"/\\|?*\x00-\x1f]', value)
    ):
        raise ExportError(f"{label}包含不适合文件名的字符：{value!r}")
    return value


def choose_report(lab: Path, week: int, args: argparse.Namespace, pdfs: list[Path]) -> Path:
    if args.report:
        report = (lab / args.report).resolve()
        if report not in pdfs:
            raise ExportError("--report 必须指向此 Lab 的 docs/pdf 内现有的 PDF 文件。")
        return report
    matching = []
    for pdf in pdfs:
        match = REPORT_NAME.fullmatch(pdf.stem)
        if (
            match and int(match["week"]) == week
            and (not args.student_id or args.student_id == match["student_id"])
            and (not args.name or args.name == match["name"])
        ):
            matching.append(pdf)
    if len(matching) == 1:
        return matching[0]
    if len(pdfs) == 1:
        return pdfs[0]
    if not pdfs:
        raise ExportError("docs/pdf 中没有 PDF；请先将实验报告导出为 PDF。")
    choices = "\n  ".join(str(p.relative_to(lab)) for p in pdfs)
    raise ExportError(f"无法唯一确定实验报告，请用 --report 指定：\n  {choices}")


def make_plan(args: argparse.Namespace) -> ExportPlan:
    lab = Path(args.lab).expanduser()
    if not lab.exists():
        lab = LAB_DIRECTORY / lab
    lab = lab.resolve()
    if not lab.is_dir():
        raise ExportError(f"Lab 文件夹不存在：{lab}")
    week_match = re.fullmatch(r"week([1-9]\d*)", lab.name, re.IGNORECASE)
    if not week_match:
        raise ExportError("Lab 文件夹应命名为 week1、week2 等（周次不补零）。")
    week = int(week_match[1])
    pdfs = [
        p for p in walk_files(lab / "docs" / "pdf", set(), include_hidden=True)
        if p.suffix.lower() == ".pdf"
    ]
    report = choose_report(lab, week, args, pdfs)
    metadata = REPORT_NAME.fullmatch(report.stem)
    if metadata and int(metadata["week"]) != week:
        raise ExportError(f"报告周次 week_{int(metadata['week'])} 与文件夹 {lab.name} 不一致。")
    student_id = args.student_id or (metadata["student_id"] if metadata else None)
    name = args.name or (metadata["name"] if metadata else None)
    if not student_id or not name:
        raise ExportError(
            "无法从报告名识别学号、姓名。请使用“学号-姓名-week_1.pdf”形式，"
            "或传入 --student-id 和 --name。"
        )
    if not re.fullmatch(r"[0-9]+", student_id):
        raise ExportError("学号必须只包含数字。")
    name = filename_part(name, "姓名")
    stem = f"{student_id}-{name}-week_{week}"
    if args.title is not None:
        stem += "-" + filename_part(args.title, "实验名称")

    source_files = walk_files(lab / "src")
    source_code = [p for p in source_files if is_code(p)]
    if not source_code:
        raise ExportError("src 中没有可提交的代码文件；请先完成实验代码。")
    root_code = [
        p for p in lab.iterdir()
        if p.is_file() and not p.name.startswith(".") and not is_link(p) and is_code(p)
    ]
    results = [
        p for p in walk_files(lab / "docs", EXCLUDED_DIRECTORIES | {"pdf"})
        if p.suffix.lower() in RESULT_EXTENSIONS
    ]
    if not results:
        raise ExportError("docs 中没有图片或视频结果；请先运行实验生成结果文件。")
    output = Path(args.output_dir).expanduser().resolve() / f"{stem}-提交.zip"
    if output.exists() and not args.force and not args.dry_run:
        raise ExportError(f"目标文件已存在：{output}\n如需覆盖，请加 --force。")
    return ExportPlan(
        lab, report, pdfs, stem, output, sorted(source_code + root_code), results,
        [p for p in source_files if not is_code(p)],
    )


def pdf_entries(plan: ExportPlan) -> list[tuple[Path, str]]:
    """所有 PDF 放在总包根目录；重名时加序号，避免解压覆盖。"""
    report_name = f"{plan.stem}.pdf"
    entries = [(plan.report, report_name)]
    used_names = {report_name.casefold()}
    original_names = {path.name.casefold() for path in plan.pdfs}
    pdf_directory = plan.lab / "docs" / "pdf"
    # 优先保留原本就在 docs/pdf 根目录的文件名。
    for path in sorted(plan.pdfs, key=lambda p: (len(p.relative_to(pdf_directory).parts), p)):
        if path == plan.report:
            continue
        name = path.name
        number = 2
        if name.casefold() in used_names:
            while True:
                name = f"{path.stem} ({number}){path.suffix}"
                number += 1
                if name.casefold() not in used_names | original_names:
                    break
        used_names.add(name.casefold())
        entries.append((path, name))
    return entries


def export_zip(plan: ExportPlan, *, force: bool = False) -> int:
    plan.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".export-lab-", dir=plan.output.parent) as staging:
        code_zip = Path(staging) / f"{plan.stem}.zip"
        with ZipFile(code_zip, "w", ZIP_DEFLATED, compresslevel=9, strict_timestamps=False) as archive:
            for path in plan.code:
                archive.write(path, path.relative_to(plan.lab).as_posix())
        code_size = code_zip.stat().st_size
        if code_size >= CODE_ZIP_LIMIT:
            raise ExportError(
                f"代码 ZIP 为 {code_size:,} 字节，必须小于 {CODE_ZIP_LIMIT:,} 字节；"
                "请精简代码后重试。"
            )
        submission = Path(staging) / "submission.zip"
        with ZipFile(submission, "w", ZIP_DEFLATED, compresslevel=9, strict_timestamps=False) as archive:
            for path, name in pdf_entries(plan):
                archive.write(path, name)
            archive.write(code_zip, code_zip.name, compress_type=ZIP_STORED)
            for path in plan.results:
                archive.write(path, "实验结果/" + path.relative_to(plan.lab / "docs").as_posix())
        if force:
            submission.replace(plan.output)
        else:
            # 独占创建，防止导出期间出现同名文件时被意外覆盖。
            created = False
            try:
                with plan.output.open("xb") as target:
                    created = True
                    with submission.open("rb") as source:
                        shutil.copyfileobj(source, target)
            except FileExistsError:
                raise ExportError(f"目标文件已存在：{plan.output}；如需覆盖，请加 --force。") from None
            except BaseException:
                if created:
                    plan.output.unlink(missing_ok=True)
                raise
    return code_size


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lab", help="Lab 文件夹路径或 Lab 下的文件夹名，例如 week1")
    parser.add_argument("--title", help="可选实验名称；指定时追加到文件名，默认只使用学号-姓名-week_x")
    parser.add_argument("--report", help="指定用于识别姓名、学号并重命名的主报告；docs/pdf 内所有 PDF 仍会打包")
    parser.add_argument("--student-id", help="手动指定学号，默认从报告文件名识别")
    parser.add_argument("--name", help="手动指定姓名，默认从报告文件名识别")
    parser.add_argument("-o", "--output-dir", default=str(EXPORT_DIRECTORY), help="输出目录，默认脚本所在的 Lab/exports")
    parser.add_argument("--force", action="store_true", help="覆盖同名导出文件")
    parser.add_argument("--dry-run", action="store_true", help="仅查看文件清单，不生成 ZIP；实际导出时检查代码包大小")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = argument_parser().parse_args(argv)
    try:
        plan = make_plan(args)
        print(f"实验报告：{plan.report.relative_to(plan.lab)}")
        print("全部 PDF 文件：")
        for path, name in pdf_entries(plan):
            print(f"  {path.relative_to(plan.lab)} -> {name}")
        print("代码文件：")
        for path in plan.code:
            print(f"  {path.relative_to(plan.lab)}")
        print("结果文件：")
        for path in plan.results:
            print(f"  {path.relative_to(plan.lab)}")
        if plan.skipped_code:
            print("src 中以下文件不属于支持的代码类型，已排除：")
            for path in plan.skipped_code:
                print(f"  {path.relative_to(plan.lab)}")
        print(f"输出路径：{plan.output}")
        if args.dry_run:
            print("预览完成，未生成 ZIP。")
        else:
            code_size = export_zip(plan, force=args.force)
            print(f"导出成功。代码 ZIP：{code_size:,} 字节（小于 10 MB）。")
        return 0
    except (ExportError, OSError) as error:
        print(f"导出失败：{error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
