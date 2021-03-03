"""Luminate Service charges"""
from finance_manager.database.replaceable import ReplaceableObject as o


sql = f"""
SELECT s.costc, s.description, SUM(ISNULL(i.amount,0)) as amount, c.directorate_id, f.set_cat_id, f.acad_year
FROM f_set f
INNER JOIN fs_cost_centre c ON f.costc = c.costc
CROSS JOIN conf_shared_service s
LEFT OUTER JOIN 
    (SELECT i.costc, SUM(i.amount) as amount, i.set_id
    FROM input_nonp_internal i
    WHERE i.amount <> 0 AND account = 4371
    GROUP BY i.costc, i.set_id)
    i ON s.costc = i.costc AND i.set_id = f.set_id
WHERE f.surpress = 0
GROUP BY s.costc, s.description, c.directorate_id, f.set_cat_id, f.acad_year
"""


def _view():
    return o("v_luminate_service", sql)
