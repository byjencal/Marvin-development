import unittest


class TestPep257(unittest.TestCase):

    def test_pep257(self):
        """Test that Python files conform to pep257 docstring style."""
        import os
        import subprocess

        result = subprocess.run(
            ['pydocstyle', '--ignore=D104,D203,D213', os.path.dirname(__file__)],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
