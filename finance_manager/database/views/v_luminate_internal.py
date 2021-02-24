"""Luminate internal income"""
from finance_manager.database.replaceable import ReplaceableObject as o


sql = f"""
SELECT c.directorate_id, f.set_cat_id, f.acad_year, c.costc, c.description as costc_description, 
	CASE a.default_balance WHEN 'CR' THEN i.amount ELSE 0 END as income, 
	CASE a.default_balance WHEN 'DR' THEN i.amount ELSE 0 END as expenditure, 
	i.description
FROM v_input_nonp_internal i 
INNER JOIN fs_account a ON a.account = i.account 
INNER JOIN fs_cost_centre c ON i.costc = c.costc 
INNER JOIN f_set f ON f.set_Id = i.set_id 
WHERE a.summary_code in (302, 503) AND i.net = 0
AND f.surpress = 0
"""


def _view():
    return o("v_luminate_internal", sql)
