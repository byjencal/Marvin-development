import unittest


class TestFlake8(unittest.TestCase):

    def test_flake8(self):
        """Test that Python files conform to flake8 style."""
        import os
        import subprocess

        result = subprocess.run(
            ['flake8', '--exclude=.venv,build,install,log', os.path.dirname(__file__)],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
