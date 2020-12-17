from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.functions import periods

staff_month_ni = ", \n".join(
    [f"ISNULL(dbo.udfNI(mt.p{n}, ni.p{n}, ni.rate)*m.p{n}/NULLIF(ISNULL(NULLIF(mt.p{n},0),m.p{n}),0),0) as ni_p{n}" for n in periods()])
staff_month_pension = ", \n".join(
    [f"m.p{n}*ISNULL(pension.p{n},0) as pension_p{n}" for n in periods()])
staff_travel_months = 12
staff_travel_allowance = ", \n ".join(
    [f"ISNULL(s.travel_scheme,0)/{staff_travel_months} as travel_p{n}" for n in periods()])


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
