"""View for reporting using the student-friendly categorisation."""
from finance_manager.database.replaceable import ReplaceableObject as o


sql = f"""
SELECT v.*, s.acad_year, s.costc, CAST(s.acad_year as CHAR(4)) + ' ' + s.set_cat_id as finance_summary, c.directorate_id 
FROM v_mri_finance_grouped_subtotal v
INNER JOIN f_set s ON v.set_id = s.set_id 
INNER JOIN fs_cost_centre c on c.costc = s.costc
"""


def _view():
    return o("v_luminate_finance", sql)
