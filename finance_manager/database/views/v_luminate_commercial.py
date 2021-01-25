"""Luminate commercial income table"""
from finance_manager.database.replaceable import ReplaceableObject as o


sql = f"""
SELECT c.directorate_id, s.acad_year, s.set_cat_id, c.costc + ' ' + x.description as description, x.amount
FROM 
(
	--Courses
	SELECT set_id, course_name as description, total as amount FROM v_input_inc_courses
		WHERE total <> 0
	UNION ALL
	--Other
	SELECT set_id, i.description, SUM(amount) as amount 
		FROM v_input_inc_other i INNER JOIN fs_account a on a.account = i.account 
		WHERE a.summary_code = 104
		GROUP BY set_id, i.description 
		Having SUM(amount) <> 0
	) x 
INNER JOIN f_set s ON x.set_id = s.set_id 
INNER JOIN fs_cost_centre c ON c.costc = s.costc 
"""


def _view():
    return o("v_luminate_commercial", sql)
