"""
Checks that the database specification doesn't throw any obvious errors
"""
import unittest

from finance_manager.database import views


class TestViews(unittest.TestCase):
    def test_get_headers(self):
        """
        Check header reading works. 
        """
        sql = """SELECT a.first, SUM(fdsaf.x + ISNULL(f.y, 0)) as second,   
                SUM(CASE WHEN af.period = c.split_at_period THEN ISNULL(af.amount,0) ELSE 0 END)
			as third FROM something"""
        self.assertEqual(views.get_headers(sql), ["first", "second", "third"])


if __name__ == "__main__":
    unittest.main()
