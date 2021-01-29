"""
Checking the package's UDFs. 
"""
import unittest
from finance_manager import functions


class TestFunctions(unittest.TestCase):
    def test_normalise_period(self):
        """
        Check the period normalising function.   
        """
        # Check it didn't error
        self.assertEqual(functions.normalise_period("P6"), 6)
        self.assertEqual(functions.normalise_period(202106), 6)

    def test_period_to_month(self):
        self.assertEqual(functions.period_to_month(10, 2007), (5, 2008))
        self.assertEqual(functions.period_to_month(13, 2007), (8, 2008))
        self.assertEqual(functions.period_to_month(0, 2007), (7, 2007))


if __name__ == "__main__":
    unittest.main()
