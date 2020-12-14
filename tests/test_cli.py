"""
Checks that the database specification doesn't throw any obvious errors
"""
import unittest
from click.testing import CliRunner
from finance_manager.cli import fm


class TestCLI(unittest.TestCase):
    def test_fm(self):
        """
        Check the CLI runs without error. This will fail if any of the subcommands do not compile right.   
        """
        runner = CliRunner()
        result = runner.invoke(fm, ["--help"])
        # Check it didn't error
        self.assertEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
