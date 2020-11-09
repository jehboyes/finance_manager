from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views import staff_month_sal


def _view():
    v = o("v_calc_staff_monthly", f"""
SELECT s.staff_line_id, s.post_status_id, s.set_id, f_set.acad_year, f_set.set_cat_id, ISNULL(s.staff_id, s.staff_line_id) as staff_id,
{staff_month_sal}
FROM input_pay_staff s
INNER JOIN f_set ON f_set.set_id = s.set_id
LEFT OUTER JOIN staff_spine ss on ss.spine = s.current_spine
INNER JOIN v_calc_staff_fte vFTE on vFTE.staff_line_id = s.staff_line_id
""")
    return v
