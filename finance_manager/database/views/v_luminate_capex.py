"""Luminate capex"""
from finance_manager.database.replaceable import ReplaceableObject as o


sql = f"""
SELECT v.*, f.set_cat_id, f.acad_year, 'E' as directorate_id 
FROM v_input_capex v
INNER JOIN f_set f ON f.set_id = v.set_id 
INNER JOIN fs_cost_centre cc ON cc.costc = f.costc 
WHERE f.surpress = 0 AND v.total_amount > 0
"""


def _view():
    return o("v_luminate_capex", sql)
