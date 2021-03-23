"""Luminate staffing"""
from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views import _generate_p_string

periods = _generate_p_string(
    "p{p}", ", ")


sql = f"""
SELECT s.luminate_description as status, v.name, v.title, t.lcc_description as type, indicative_fte as fte,  
	v.grade, v.current_spine as spine, p.description as pension, 
	ISNULL(pay_total,0) + ISNULL(ni_total,0)+ ISNULL(pension_total,0) + ISNULL(travel_scheme,0) as amount, 
	{periods}, 
	f.set_cat_id, f.acad_year, f.costc, cc.directorate_id 
FROM v_input_pay_staff v
	INNER JOIN staff_post_type t ON t.post_type_id = v.post_type_id 
	INNER JOIN staff_post_status s ON s.post_status_id = v.post_status_id
	INNER JOIN staff_pension p ON p.pension_id = v.pension_id
	INNER JOIN f_set f ON f.set_id = v.set_id 
	INNER JOIN fs_cost_centre cc ON cc.costc = f.costc 
WHERE s.exclude_from_finance <> 1
AND f.surpress = 0
"""


def _view():
    return o("v_luminate_staff", sql)
