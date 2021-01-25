from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.functions import periods
from finance_manager.database.views import _generate_p_string

# work out a line's monthly salary
staff_month_sal = _generate_p_string(
    """dbo.udfGetMonthProp(f_set.acad_year, {p}, s.start_date, s.end_date)
            *vFTE.FTE
            *(
                ISNULL(dbo.udfGetMonthSpine(f_set.acad_year, {p}, s.start_date, s.current_spine, s.grade, f_set.set_cat_id),0)
                +ISNULL(s.allowances,0)
            )/12 as p{p}""", ", \n")
# get actual spine point for displaying in app
staff_month_sp = _generate_p_string(
    "dbo.udfGetMonthSpinePoint(f_set.acad_year, {p}, s.start_date, s.current_spine, s.grade) as sp_p{p}", ", \n")


def _view():
    v = o("v_calc_staff_monthly", f"""
SELECT s.staff_line_id, s.post_status_id, s.set_id, f_set.acad_year, f_set.set_cat_id, ISNULL(s.staff_id, s.staff_line_id) as staff_id,
{staff_month_sal},
{staff_month_sp}
FROM input_pay_staff s
INNER JOIN f_set ON f_set.set_id=s.set_id
LEFT OUTER JOIN staff_spine ss on ss.spine=s.current_spine AND f_set.acad_year=ss.acad_year AND f_set.set_cat_id=ss.set_cat_id
INNER JOIN v_calc_staff_fte vFTE on vFTE.staff_line_id=s.staff_line_id
""")
    return v
