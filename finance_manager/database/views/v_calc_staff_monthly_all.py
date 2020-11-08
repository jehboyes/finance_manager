from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views import staff_month_ni, staff_month_pension, staff_travel_allowance


def _view():
    v = o("v_calc_staff_monthly_all", f"""
SELECT m.*,
{staff_month_ni},
{staff_month_pension},
{staff_travel_allowance}
FROM v_calc_staff_monthly m
INNER JOIN v_calc_staff_monthly_total mt ON m.staff_Id = mt.staff_id
                                         AND m.acad_year = mt.acad_year
                                         AND m.set_cat_id = mt.set_cat_id
INNER JOIN input_pay_staff s ON s.staff_line_id = m.staff_line_id
LEFT OUTER JOIN staff_pension_contrib pension ON pension.pension_id = s.pension_id AND pension.acad_year = m.acad_year
INNER JOIN staff_ni ni ON ni.acad_year = m.acad_year
""")
    return v
