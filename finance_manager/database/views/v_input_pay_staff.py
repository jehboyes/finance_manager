from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.functions import periods
from finance_manager.database.views import _generate_p_string
# Total figures
staff_total_pay = "+".join([f"a.p{n}" for n in periods()])
staff_total_ni = "+".join([f"a.ni_p{n}" for n in periods()])
staff_total_pension = "+".join([f"a.pension_p{n}" for n in periods()])

periods = _generate_p_string(
    "a.p{p} + a.ni_p{p} + a.pension_p{p} + a.travel_p{p} as p{p}", ", \n")

sql = f"""
SELECT s.*, 
    sps.description as post_status_desc, 
    sps.colour_hex as hex,
    spt.description as post_type_desc,
    sp.description as pension_desc, 
    sct.description as con_desc, 
{staff_total_pay} as pay_total,
{staff_total_ni} as ni_total,
{staff_total_pension} as pension_total, 
    {staff_total_pay} + {staff_total_ni} + {staff_total_pension} + ISNULL(travel_scheme,0) as total, 
    {periods}
FROM input_pay_staff AS s
LEFT OUTER JOIN v_calc_staff_monthly_all a ON a.staff_line_id = s.staff_line_id
LEFT OUTER JOIN staff_post_status sps ON sps.post_status_id = s.post_status_id
LEFT OUTER JOIN staff_post_type spt ON spt.post_type_id = s.post_type_id 
LEFT OUTER JOIN staff_pension sp ON sp.pension_id = s.pension_id
INNER JOIN f_set f ON f.set_id = s.set_id
LEFT OUTER JOIN staff_con_type sct ON sct.con_type_id = s.con_type_id 
                                    AND sct.acad_year = f.acad_year
                                    AND sct.set_cat_id = f.set_cat_id
"""


def _view():
    return o("v_input_pay_staff", sql)
