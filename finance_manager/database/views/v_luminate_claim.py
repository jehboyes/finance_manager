"""Luminate claims"""
from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views import _generate_p_string

periods = _generate_p_string(
    "c.p{p}*c.adjusted_rate + c.ni_p{p} + c.pension_p{p} as P{p}", ", \n")
period_sum = _generate_p_string("v.p{p}", "+")

sql = f"""
SELECT 'N/A' as name, 'N/A' as title,  {period_sum}  as hours, c.adjusted_rate as rate, v.amount,
	v.description, 
	{periods}, f.set_cat_id, f.acad_year, cc.directorate_id 
FROM v_input_pay_claim v
INNER JOIN v_calc_claim c ON c.claim_id = v.claim_id 
INNER JOIN f_set f ON f.set_id = v.set_id
INNER JOIN fs_cost_centre cc ON cc.costc = f.costc
WHERE v.amount <> 0
AND f.surpress = 0
"""


def _view():
    return o("v_luminate_claim", sql)
