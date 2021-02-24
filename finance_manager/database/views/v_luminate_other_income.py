"""Luminate project income table"""
from finance_manager.database.replaceable import ReplaceableObject as o


sql = f"""
SELECT c.directorate_id, s.acad_year, s.set_cat_id, c.costc + ' ' + x.description as description, x.amount
FROM 
(
	SELECT set_id, i.description, SUM(amount) as amount 
		FROM v_input_inc_other i INNER JOIN fs_account a on a.account = i.account 
		WHERE a.summary_code in (107,108)
		GROUP BY set_id, i.description 
		HAVING SUM(amount) <> 0
	) x 
INNER JOIN f_set s ON x.set_id = s.set_id 
INNER JOIN fs_cost_centre c ON c.costc = s.costc 
WHERE s.surpress = 0
"""


def _view():
    return o("v_luminate_other_income", sql)
