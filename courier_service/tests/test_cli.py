from pathlib import Path
import sqlite3
import subprocess
import sys
import sysconfig
from tempfile import TemporaryDirectory
import unittest


class CliTests(unittest.TestCase):
    def run_example(self, command):
        with TemporaryDirectory() as directory:
            result = subprocess.run(
                command, cwd=directory, capture_output=True, text=True, timeout=20,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Tracking number:", result.stdout)
            database = Path(directory) / "shipments.sqlite3"
            self.assertTrue(database.is_file())
            connection = sqlite3.connect(database)
            try:
                self.assertEqual(connection.execute(
                    "SELECT COUNT(*) FROM shipments"
                ).fetchone()[0], 1)
                self.assertEqual(connection.execute(
                    "SELECT status FROM dispatches"
                ).fetchone()[0], "NOTIFIED")
            finally:
                connection.close()

    def test_module_entrypoint_from_another_directory(self):
        self.run_example([sys.executable, "-m", "courier_service"])

    def test_main_wrapper(self):
        wrapper = Path(__file__).resolve().parents[1] / "main.py"
        self.run_example([sys.executable, str(wrapper)])

    def test_installed_console_command(self):
        filename = "courier-dispatch.exe" if sys.platform == "win32" else "courier-dispatch"
        command = Path(sysconfig.get_path("scripts")) / filename
        self.assertTrue(command.is_file())
        self.run_example([str(command)])


if __name__ == "__main__":
    unittest.main()
