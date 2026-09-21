"""检查提交包内容、报告选择、大小边界和已有文件保护。"""

import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "exports"))
import export_lab


class ExportLabTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.lab = self.root / "week1"
        self.output = self.root / "exports"
        self.put("src/main.py", b"print('hello')\n")
        self.put("src/nested/helper.py", b"VALUE = 42\n")
        self.put("src/shaders/example.frag", b"void main() {}\n")
        self.put("requirements.txt", b"matplotlib\n")
        self.put("run.bat", b"@python src/main.py\n")
        self.report = self.put("docs/pdf/123456-测试-week_1.pdf", b"%PDF-1.4\nreport\n")
        self.put("docs/pdf/参考资料.pdf", b"%PDF-1.4\nreference\n")
        self.put("docs/images/result.PNG", b"image result")
        self.put("docs/videos/demo.mp4", b"video result")
        self.put("docs/images/nested/result.PNG", b"another image")

    def put(self, relative, content):
        path = self.lab / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def args(self, *extra):
        return export_lab.argument_parser().parse_args(
            [str(self.lab), "--output-dir", str(self.output), *extra]
        )

    def test_archive_contents_and_originals(self):
        self.put("src/__pycache__/cached.pyc", b"cache")
        self.put("src/.venv/lib/dependency.py", b"third party")
        self.put("src/venv/lib/dependency.py", b"third party")
        self.put("src/build/generated.c", b"build output")
        self.put("src/program.exe", b"binary")
        self.put("src/preview.png", b"not code")
        self.put("docs/report.md", b"draft")
        original = {p: p.read_bytes() for p in self.lab.rglob("*") if p.is_file()}
        plan = export_lab.make_plan(self.args("--title", "圆与曲线"))
        size = export_lab.export_zip(plan)
        self.assertEqual(plan.stem, "123456-测试-week_1-圆与曲线")
        with ZipFile(plan.output) as outer:
            self.assertIsNone(outer.testzip())
            self.assertEqual(set(outer.namelist()), {
                f"{plan.stem}.pdf", f"{plan.stem}.zip",
                "pdf/参考资料.pdf",
                "实验结果/images/result.PNG", "实验结果/videos/demo.mp4",
                "实验结果/images/nested/result.PNG",
            })
            self.assertEqual(outer.read(f"{plan.stem}.pdf"), original[self.report])
            self.assertEqual(outer.read("pdf/参考资料.pdf"), original[self.lab / "docs/pdf/参考资料.pdf"])
            code_bytes = outer.read(f"{plan.stem}.zip")
            self.assertEqual(size, len(code_bytes))
            with ZipFile(io.BytesIO(code_bytes)) as code:
                self.assertIsNone(code.testzip())
                self.assertEqual(set(code.namelist()), {
                    "src/main.py", "src/nested/helper.py", "src/shaders/example.frag",
                    "run.bat", "requirements.txt",
                })
                for name in code.namelist():
                    self.assertEqual(code.read(name), original[self.lab / name])
        for path, content in original.items():
            self.assertEqual(path.read_bytes(), content)

    def test_ambiguous_reports_require_explicit_selection(self):
        second = self.put("docs/pdf/123456-测试-week_1-另一个版本.pdf", b"%PDF-1.4\nother\n")
        with self.assertRaisesRegex(export_lab.ExportError, "无法唯一确定"):
            export_lab.make_plan(self.args())
        plan = export_lab.make_plan(self.args("--report", str(second.relative_to(self.lab))))
        self.assertEqual(plan.report, second)
        export_lab.export_zip(plan)
        with ZipFile(plan.output) as archive:
            self.assertEqual(archive.read(f"{plan.stem}.pdf"), second.read_bytes())
            self.assertEqual(archive.read("pdf/" + self.report.name), self.report.read_bytes())
            self.assertIn("pdf/参考资料.pdf", archive.namelist())

    def test_all_pdfs_keep_relative_paths_and_contents(self):
        extra = [
            self.put("docs/pdf/nested/参考资料.PDF", b"%PDF-1.4\nnested\n"),
            self.put("docs/pdf/another/参考资料.pdf", b"%PDF-1.4\nanother\n"),
            self.put("docs/pdf/.hidden.pdf", b"%PDF-1.4\nhidden\n"),
            self.put("docs/pdf/.drafts/draft.pdf", b"%PDF-1.4\ndraft\n"),
            self.put("docs/pdf/build/diagram.pdf", b"%PDF-1.4\ndiagram\n"),
        ]
        self.put("docs/pdf/notes.txt", b"not a PDF")
        plan = export_lab.make_plan(self.args())
        export_lab.export_zip(plan)
        with ZipFile(plan.output) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(len([n for n in archive.namelist() if n.lower().endswith(".pdf")]), 7)
            for path in extra:
                member = "pdf/" + path.relative_to(self.lab / "docs/pdf").as_posix()
                self.assertEqual(archive.read(member), path.read_bytes())
            self.assertNotIn("pdf/notes.txt", archive.namelist())

    def test_wrong_week_and_outside_report_are_rejected(self):
        wrong = self.put("docs/pdf/123456-测试-week_2.pdf", b"%PDF-1.4\nweek two\n")
        with self.assertRaisesRegex(export_lab.ExportError, "不一致"):
            export_lab.make_plan(self.args("--report", str(wrong)))
        outside = self.root / "outside.pdf"
        outside.write_bytes(b"%PDF-1.4\n")
        with self.assertRaisesRegex(export_lab.ExportError, "docs/pdf"):
            export_lab.make_plan(self.args("--report", str(outside)))

    def test_missing_materials_fail_before_export(self):
        for kind in ("report", "code", "results"):
            with self.subTest(kind=kind):
                if kind == "report":
                    files = list((self.lab / "docs/pdf").glob("*.pdf"))
                    expected = "没有 PDF"
                elif kind == "code":
                    files = [p for p in (self.lab / "src").rglob("*") if p.is_file()]
                    expected = "没有可提交的代码"
                else:
                    files = [p for p in (self.lab / "docs").rglob("*")
                             if p.suffix.lower() in export_lab.RESULT_EXTENSIONS]
                    expected = "没有图片或视频"
                content = {p: p.read_bytes() for p in files}
                try:
                    for path in files:
                        path.unlink()
                    with self.assertRaisesRegex(export_lab.ExportError, expected):
                        export_lab.make_plan(self.args())
                    self.assertFalse(self.output.exists())
                finally:
                    for path, data in content.items():
                        path.write_bytes(data)

    def test_size_limit_is_strict_and_failed_force_keeps_old_export(self):
        plan = export_lab.make_plan(self.args())
        code_size = export_lab.export_zip(plan)
        original_export = plan.output.read_bytes()
        with patch.object(export_lab, "CODE_ZIP_LIMIT", code_size):
            with self.assertRaisesRegex(export_lab.ExportError, "必须小于"):
                export_lab.export_zip(plan, force=True)
        self.assertEqual(plan.output.read_bytes(), original_export)
        self.assertEqual(list(self.output.iterdir()), [plan.output])
        with patch.object(export_lab, "CODE_ZIP_LIMIT", code_size + 1):
            self.assertEqual(export_lab.export_zip(plan, force=True), code_size)

    def test_existing_export_requires_force_even_after_planning(self):
        plan = export_lab.make_plan(self.args())
        self.output.mkdir()
        plan.output.write_bytes(b"keep existing file")
        with self.assertRaisesRegex(export_lab.ExportError, "已存在"):
            export_lab.export_zip(plan)
        self.assertEqual(plan.output.read_bytes(), b"keep existing file")
        with self.assertRaisesRegex(export_lab.ExportError, "已存在"):
            export_lab.make_plan(self.args())
        export_lab.export_zip(export_lab.make_plan(self.args("--force")), force=True)
        with ZipFile(plan.output) as archive:
            self.assertIsNone(archive.testzip())

    def test_custom_report_identity_and_invalid_title(self):
        custom = self.put("docs/pdf/报告.pdf", b"%PDF-1.4\ncustom\n")
        plan = export_lab.make_plan(self.args(
            "--report", str(custom), "--student-id", "789", "--name", "张三",
        ))
        self.assertEqual(plan.stem, "789-张三-week_1-week1")
        with self.assertRaisesRegex(export_lab.ExportError, "不适合文件名"):
            export_lab.make_plan(self.args("--title", "../outside"))

    def test_cli_dry_run_and_error_exit_status(self):
        cli_args = [str(self.lab), "--output-dir", str(self.output), "--dry-run"]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(export_lab.main(cli_args), 0)
        self.assertFalse(self.output.exists())
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors):
            self.assertEqual(export_lab.main([str(self.root / "week99")]), 1)
        self.assertIn("文件夹不存在", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
