"""
Calculates an employee's total pay in a month, to enable accurate on-cost-ing, 
or more specifically, accurate calculation of National Insurance. 
"""
from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.functions import periods


staff_month_sal_total = ", \n".join(
    [f"SUM(m.p{n}) as p{n}" for n in periods()])


def _view():
    view = o("v_calc_staff_monthly_total", f"""
SELECT m.staff_id, m.acad_year, m.set_cat_id,
{staff_month_sal_total}
FROM v_calc_staff_monthly m
LEFT OUTER JOIN staff_post_status ps ON ps.post_status_id = m.post_status_id
WHERE ps.exclude_from_finance = 0
GROUP BY m.staff_id, m.acad_year, m.set_cat_id
         """)
    return view
