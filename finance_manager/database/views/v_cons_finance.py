from finance_manager.database.replaceable import ReplaceableObject as o


sql = f"""
SELECT v.summary_code, v.directorate_id, s.acad_year, s.set_cat_id, s.costc, SUM(amount) as amount
FROM v_mri_finance v
INNER JOIN f_set s ON v.set_id = s.set_id
GROUP BY v.summary_code, v.directorate_id, s.acad_year, s.set_cat_id, s.costc
"""


def _view():
    return o("v_cons_finance", sql)
