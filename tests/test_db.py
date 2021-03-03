"""
Checks that the database specification doesn't throw any obvious errors
"""
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from finance_manager.database.views import v_luminate_finance, v_mri_finance, v_mri_finance_grouped_subtotal, v_mri_finance_grouped_subtotal_internal
from finance_manager.cli.db.syncviews import syncviews
from finance_manager.database.spec import Base


class TestPython(unittest.TestCase):
    """
    Tests for testing the python functions used for constructing views
    """

    def test_get_headers(self):
        """
        Tests function that extracts header names from SQL SELECT statement.
        """
        sql = """SELECT a.first, SUM(fdsaf.x + ISNULL(f.y, 0)) as second,
                SUM(CASE WHEN af.period = c.split_at_period THEN ISNULL(af.amount,0) ELSE 0 END)
			as third FROM something"""
        self.assertEqual(v.get_headers(sql), ["first", "second", "third"])


class TestViews(unittest.TestCase):

    def setUp(self):
        # In memory database for testing
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)

    def test_v_luminate_finance(self):
        views = [v_mri_finance,
                 v_mri_finance_grouped_subtotal,
                 v_mri_finance_grouped_subtotal_internal,
                 v_luminate_finance]
        for v in views:
            self.engine.execute(
                f"CREATE VIEW {v._view().name} AS {v._view().sqltext}".replace("ISNULL", "IFNULL"))
        self.assertEqual(1, 1)


if __name__ == "__main__":
    unittest.main()
