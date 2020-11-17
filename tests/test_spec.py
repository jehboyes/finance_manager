"""
Checks that the database specification doesn't throw any obvious errors
"""
import unittest

from finance_manager.database import spec


class TestSpec(unittest.TestCase):
    def test_table_map(self):
        """
        Check the table map compilation runs, and produces the right output. Testing on pension table for simplicity. 
        """
        self.maxDiff = None
        pension_doc = """
        Actual table name: ``staff_pension``
        Pension schemes.
        A pension scheme, relevant because of employer's contributions. See :term:`On-costs` for more detail.
        Attributes
        ----------
        pension_id : str [**PK**]
            ID of the pension scheme.
        description : str
            Diplay name of the pension scheme.""".split()
        actual_doc = spec.pension.__doc__.split()
        # Check docstrings specifically
        self.assertEqual(actual_doc, pension_doc)
        # Check the table_map functions properly
        self.assertEqual(spec.table_map["staff_pension"], spec.pension)


if __name__ == "__main__":
    unittest.main()
