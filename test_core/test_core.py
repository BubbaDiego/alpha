from __future__ import annotations

import sys
import contextlib
import os
import importlib
import re
import subprocess
from pathlib import Path
import pytest
from core.core_imports import log

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    console = Console()
except Exception:
    Console = None
    Panel = None
    Table = None
    console = None


class TestCore:
    """Utility to run pytest with rich reporting."""

    def __init__(self, report_dir: str | Path = "reports", default_pattern: str = "tests/test_*.py") -> None:
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(exist_ok=True)
        self.default_pattern = default_pattern


    def run_all(self) -> None:
        self.run_glob(self.default_pattern)


    
    def expand_pattern(self, raw: str) -> str:
        """Expand user input to a valid test glob pattern. E.g., 'twi' -> 'test_twi*.*'"""
        if "*" in raw or raw.startswith("test_"):
            return raw
        return f"test_{raw}*.*"

    def run_glob(self, pattern: str | None = None) -> None:

        pattern = self.expand_pattern(pattern or self.default_pattern)
        files = [
            p for p in Path(".").rglob(pattern)
            if not any(part in {".venv", "venv", "site-packages", "__pycache__"} for part in p.parts)
            and p.suffix == ".py"
        ]
        if not files:
            log.warning(f"⚠️ No test files found for pattern: {pattern}", source="TestCore")
            return
        self.run_files(files)

    def run_files(self, files: list[str | Path]) -> None:
        html_report = self.report_dir / "last_test_report.html"
        json_report = self.report_dir / "last_test_report.json"
        txt_log = self.report_dir / "last_test_log.txt"

        file_paths = [
            Path(f) for f in files
            if Path(f).suffix == ".py"
            and "__pycache__" not in Path(f).parts
            and not str(f).endswith(".pyc")
        ]

        log.banner(f"🧪 Test Run Started ({len(file_paths)} file(s))")
        log.info(f"⏱ Running: {[str(f) for f in file_paths]}", source="TestCore")

        args = [*[str(f) for f in file_paths], "-vv", "-s", "--tb=short", "-rA"]

        for plugin in ["pytest_sugar", "pytest_spec", "pytest_console_scripts"]:
            if importlib.util.find_spec(plugin) is not None:
                args.extend(["-p", plugin])

        if importlib.util.find_spec("pytest_html") is not None:
            args.extend(["--html", str(html_report), "--self-contained-html"])

        if importlib.util.find_spec("pytest_jsonreport") is not None:
            args.extend(["--json-report", f"--json-report-file={json_report}"])

        os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

        with open(txt_log, "w", encoding="utf-8") as f, \
             contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
            result = pytest.main(args)

        passed = failed = skipped = 0
        summary_lines = []
        try:
            pattern = re.compile(r"(PASSED|FAILED|ERROR|SKIPPED)\s+(\S+::\S+)")
            with open(txt_log, "r", encoding="utf-8") as lf:
                for line in lf:
                    match = pattern.search(line)
                    if match:
                        outcome, test_id = match.groups()
                        summary_lines.append(f"{test_id} {outcome}")
                        if outcome == "PASSED":
                            passed += 1
                        elif outcome in ("FAILED", "ERROR"):
                            failed += 1
                        elif outcome == "SKIPPED":
                            skipped += 1
        except Exception as e:
            log.error(f"Failed to parse log summary: {e}", source="TestCore")

        for line in summary_lines:
            if line.endswith("PASSED"):
                log.success(f"✅ {line}", source="TestCore")
            elif line.endswith("FAILED") or line.endswith("ERROR"):
                log.error(f"❌ {line}", source="TestCore")
            elif line.endswith("SKIPPED"):
                log.warning(f"⚠️ {line}", source="TestCore")


        total = passed + failed + skipped
        final_grade: Optional[str] = None
        grade_color = "white"

        log.banner("Test Summary")
        log.info(f"✅ Passed: {passed}  ❌ Failed: {failed}  ⚠️ Skipped: {skipped}", source="TestCore")


        total = passed + failed + skipped
        final_grade = None
        if total:
            pct = passed / total * 100
            log.info(f"🔢 Pass Rate: {pct:.1f}% ({passed}/{total})", source="TestCore")

            # Add grade
            if pct == 100:
                grade = "A+"
                color = "green"
            elif pct >= 90:
                grade = "A"
                color = "green"
            elif pct >= 80:
                grade = "B"
                color = "orange1"
            elif pct >= 70:
                grade = "C"
                color = "yellow1"
            elif pct >= 60:
                grade = "D"
                color = "red"
            else:
                grade = "F"
                color = "red"
            final_grade = f"[bold {color}]🎓 FINAL GRADE: {grade} ({pct:.1f}%) [/bold {color}]"
            log.info(f"🎓 Grade: {grade}", source="TestCore")

        if total:
            pct = passed / total * 100
            if pct == 100:
                grade = "A+"
                grade_color = "green"
            elif pct >= 90:
                grade = "A"
                grade_color = "green"
            elif pct >= 80:
                grade = "B"
                grade_color = "orange1"
            elif pct >= 70:
                grade = "C"
                grade_color = "yellow1"
            elif pct >= 60:
                grade = "D"
                grade_color = "red"
            else:
                grade = "F"
                grade_color = "red"
            final_grade = f"[bold {grade_color}]🎓 FINAL GRADE: {grade} ({pct:.1f}%) [/bold {grade_color}]"
            log.info(f"🎓 Grade: {grade}", source="TestCore")

        if result == 0:
            log.success("✅ All tests completed!", source="TestCore")
        else:
            log.error("❌ Test run failed.", source="TestCore")
            try:
                with open(txt_log, "r", encoding="utf-8") as lf:
                    last_lines = lf.readlines()[-20:]
                print("\n==== ERROR DETAILS ====")
                for line in last_lines:
                    print(line.rstrip())
                print("=======================\n")
            except Exception as e:
                log.error(f"Failed to read log file: {e}", source="TestCore")

        log.info(f"📄 HTML Report: {html_report}", source="TestCore")
        log.info(f"🪵 Log File:    {txt_log}", source="TestCore")
        self._open_html_report(html_report)

        if final_grade and console:
            console.print("\n\n")

            console.rule("[bold white]Final Score[/bold white]", style=grade_color)
            console.print(final_grade, justify="center")
            console.rule(style=grade_color)
            console.print("\n\n")

            console.rule("[bold white]Final Score[/bold white]", style=color)
            console.print(final_grade, justify="center")
            console.rule(style=color)
            console.print("\n\n")

    def test_alert_core(self) -> None:
        self.run_glob("alert_core/**/test_*.py")

    def pick_and_run_tests(self) -> None:
        tests = [
            p for p in Path("tests").rglob("test_*.py")
            if not any(part in {".venv", "venv", "site-packages"} for part in p.parts)
        ]
        if not tests:
            print("No tests found.")
            return
        tests = sorted(tests)
        for i, t in enumerate(tests, 1):
            print(f"{i}) {t}")
        choice = input("Select tests (e.g., 1,2,7) or 'q' to cancel: ").strip()
        if not choice or choice.lower() == "q":
            return
        nums = re.findall(r"\d+", choice)
        selected = []
        for n in nums:
            idx = int(n) - 1
            if 0 <= idx < len(tests):
                selected.append(tests[idx])
        selected = list(dict.fromkeys(selected))
        if not selected:
            print("No valid selections.")
            return
        print("Running selected tests:")
        for s in selected:
            print(f"- {s}")
        self.run_files(selected)

    def setup_environment(self) -> None:
        """Install project dependencies for the test suite."""
        req_file = Path("requirements.txt")
        if not req_file.exists():
            log.error("requirements.txt not found", source="TestCore")
            return
        log.banner("Installing test dependencies")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
            log.success("Dependencies installed", source="TestCore")
        except Exception as e:  # pragma: no cover - network issues may occur
            log.error(f"Dependency installation failed: {e}", source="TestCore")


    def _open_html_report(self, report_path: Path) -> None:
        if not report_path.exists():
            return
        try:
            import webbrowser
            webbrowser.open(report_path.resolve().as_uri())
        except Exception:
            pass

    def interactive_menu(self) -> None:
        while True:
            if console:
                console.clear()
                console.print(Panel("[bold magenta]🔍 Test Runner Console[/bold magenta]", border_style="magenta"))
                table = Table(show_header=False, box=None)
                table.add_column("#", style="cyan", justify="right")
                table.add_column("Action", style="white")
                table.add_row("1", "📚 Run all tests")
                table.add_row("2", "🗂️ Run test file pattern")
                table.add_row("3", "🧪 Run Alert Core tests")
                table.add_row("4", "🎯 Pick tests to run")
                table.add_row("5", "⚙️ Install test dependencies")
                table.add_row("6", "❌ Exit")
                console.print(table)
                choice = console.input("Choose > ").strip()
            else:
                os.system("cls" if os.name == "nt" else "clear")
                print("\n=== 🔍 Test Runner Console ===")
                print("1) 📚 Run all tests")
                print("2) 🗂️ Run test file pattern")
                print("3) 🧪 Run Alert Core tests")
                print("4) 🎯 Pick tests to run")
                print("5) ⚙️ Install test dependencies")
                print("6) ❌ Exit")
                choice = input("Choose > ").strip()

            if choice == "1":
                self.run_glob()
            elif choice == "2":
                pattern_prompt = "Pattern (e.g., tests/test_*.py): "
                pattern = console.input(pattern_prompt).strip() if console else input(pattern_prompt).strip()
                self.run_glob(pattern)
            elif choice == "3":
                self.test_alert_core()
            elif choice == "4":
                self.pick_and_run_tests()
            elif choice == "5":
                self.setup_environment()
            elif choice == "6":
                break
            else:
                if console:
                    console.print("[red]Invalid choice. Try again.[/red]")
                else:
                    print("Invalid choice. Try again.")
                continue

            if console:
                console.input("\n[grey]Press ENTER to return...[/grey]")
            else:
                input("\nPress ENTER to return...")
