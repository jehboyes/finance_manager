from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.functions import periods

# Total figures
staff_total_pay = "+".join([f"a.p{n}" for n in periods()])
staff_total_ni = "+".join([f"a.ni_p{n}" for n in periods()])
staff_total_pension = "+".join([f"a.pension_p{n}" for n in periods()])


sql = f"""
SELECT s.*, 
{staff_total_pay} as pay_total,
{staff_total_ni} as ni_total,
{staff_total_pension} as pension_total
FROM input_pay_staff AS s
LEFT OUTER JOIN v_calc_staff_monthly_all a ON a.staff_line_id = s.staff_line_id
"""


def _view():
    return o("v_input_pay_staff", sql)
