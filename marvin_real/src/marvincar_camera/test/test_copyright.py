import unittest


class TestCopyright(unittest.TestCase):

    def test_copyright(self):
        """Test that all Python files have copyright headers."""
        import os
        import subprocess

        result = subprocess.run(
            ['flake8', '--select=E999', os.path.dirname(__file__)],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
