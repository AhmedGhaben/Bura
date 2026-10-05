"""Checks that the game logic stays independent of the user interface."""

import os
import subprocess
import sys
import unittest


class ArchitectureTests(unittest.TestCase):
    """Guard the separation between game logic and Pygame."""

    def test_logic_does_not_import_pygame(self) -> None:
        code: str = (
            "import sys\n"
            "import bura.cards, bura.deck, bura.rules\n"
            "print('pygame' in sys.modules)\n"
        )
        env: dict[str, str] = {**os.environ, "PYTHONPATH": os.pathsep.join(sys.path)}
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            check=True,
            env=env,
        )
        self.assertEqual(result.stdout.strip(), "False")


if __name__ == "__main__":
    unittest.main()