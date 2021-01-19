"""View for reporting using the student-friendly categorisation."""
from finance_manager.database.replaceable import ReplaceableObject as o


sql = f"""
SELECT f.acad_year, f.description as set_cat, a.default_balance, r.description as rep_cat, s.description as sum_code, 
	SUM(f.amount) as amount 
FROM v_mri_finance f
INNER JOIN fs_account a ON a.account = f.account 
INNER JOIN fs_reporting_cat_config c ON c.costc = f.costc and c.account = a.account 
INNER JOIN fs_reporting_cat r ON r.rep_cat_id = c.rep_cat_id 
INNER JOIN fs_summary_code s ON s.summary_code = a.summary_code 
WHERE r.rep_cat_id <> 99
GROUP BY f.acad_year, f.description, a.default_balance, r.description, s.description 
HAVING SUM(f.amount) <> 0
"""


def _view():
    return o("_v_mri_finance_reporting", sql)
