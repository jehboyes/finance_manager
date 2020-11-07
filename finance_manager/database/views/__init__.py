"""
Contains defintions for the more complex views, i.e. those which explicitly reference multiple period columns

Handy strings are at the top, then actual views are defined as replacable objects (in `views` list). 
Slowly moving all views to their own files, which each contain one view: files are read by importing them using importlib. 

TODO Split this file into grouped versions
"""
import importlib
from os import listdir, path

from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.functions import periods

# List of named periods
p = [f'p{n}' for n in periods()]
# p1 + ... + p12
p_sum_string = "+".join(p)
# p1, ... , p12
p_list_string = ", ".join(p)
# Shorthand, as needs to be standardised
account_description = "a.account + ' ' + a.description as account_description"
# for a period table
values_clause = ", ".join([f"({n})" for n in periods()])


def sql_bound(max_or_min, *fields):
    """
    Produces sql to return the maximum of two fields. 
    """
    cmd = max_or_min.upper()
    if cmd != "MAX" and cmd != "MIN":
        raise ValueError("Invalid command: must be MAX or MIN")
    field_str = ",".join([f"({field})" for field in fields])
    sql = f"SELECT {max_or_min}(n) FROM (VALUES {field_str}) as value(n)"
    return sql


def generate_p_string(str_format, join_with=None, restrict=None):
    """Generates a list of periods in the given format.

    Use {n} where the period numebr is required in the format string. 

    Parameters
    ----------
    format : str
        String to format with the period number.
    join_with : str
        If passed, joins the list with the given path
    restrict : int 
        If n passed, restricts the output to the first n periods 
    """
    if restrict is None:
        restrict = 12
    lst = [str_format.format(p=n) for n in periods(restrict)]
    if join_with is not None:
        lst = join_with.join(lst)
    return lst


# Detect views defined in directory
p = path.dirname(__file__)
files = listdir(p)
modules = [importlib.import_module(
    ".."+f[:-3], "finance_manager.database.views.") for f in files if f[:2] == "v_" and f != 'v_ui_finance.py']
view_list = [module.view for module in modules]

# work out a line's monthly FTE
staff_month_sal = ", \n".join(
    [f"dbo.udfGetMonthProp(f_set.acad_year, {n}, s.start_date, s.end_date)*vFTE.FTE*(ss.value+ISNULL(s.allowances,0))/12 as p{n}"
     for n in periods()])
staff_month_sal_total = ", \n".join(
    [f"SUM(m.p{n}) as p{n}" for n in periods()])
staff_month_ni = ", \n".join(
    [f"ISNULL(dbo.udfNI(mt.p{n}, ni.p{n}, ni.rate)*m.p{n}/NULLIF(ISNULL(NULLIF(mt.p{n},0),m.p{n}),0),0) as ni_p{n}" for n in periods()])
staff_month_pension = ", \n".join(
    [f"m.p{n}*ISNULL(pension.p{n},0) as pension_p{n}" for n in periods()])
staff_travel_months = 9
staff_travel_allowance = ", \n ".join(
    [f"s.travel_scheme/{staff_travel_months} as travel_p{n}" for n in range(3, 3+staff_travel_months)])


view_list += [o("v_input_pay_fracclaim", f"""
SELECT fs.set_id, ISNULL(fc.hours, 0) as hours, p.period
FROM f_set fs
CROSS JOIN
(SELECT * FROM
	(VALUES {values_clause}) AS X(period)) as p
LEFT OUTER JOIN input_pay_fracclaim fc ON fc.set_id = fs.set_id AND fc.period = p.period
"""),
              o("v_ui_finance_breakdown", f"""
SELECT set_id, summary_code, account, account_description, sum(amount) as amount FROM v_mri_finance
WHERE hide_from_users <> 1
GROUP BY set_id, summary_code, account, account_description
    """),
              o("v_input_inc_courses", f"""
SELECT *, {p_sum_string} as total
FROM input_inc_courses
    """),
              o("v_input_inc_other", f"""
SELECT i.inc_id, i.account, a.description as account_name, {account_description}, i.description, i.set_id,
{p_list_string}, {p_sum_string} as amount
FROM input_inc_other i
LEFT OUTER JOIN fs_account a ON i.account = a.account
            """),

              o("v_input_nonp_other", f"""
SELECT i.nonp_id, i.account, a.description as account_name, {account_description}, i.description, i.set_id,
{p_list_string}, {p_sum_string} as amount
FROM input_nonp_other i
LEFT OUTER JOIN fs_account a ON i.account = a.account
            """),


              o("v_fs_account", f"""
SELECT a.account, a.description, {account_description},
s.description as summary_description, s.section_id
FROM fs_account a
INNER JOIN fs_summary_code s ON s.summary_code = a.summary_code
WHERE a.hide_from_users = 0
         """),

              o("v_calc_staff_fte", f"""
SELECT staff_line_id,
   CASE s.post_type_id
      WHEN 'FRAC' THEN
            dbo.udfFracFTE((fs.curriculum_hours-ISNULL(taught.hours,0)) *
                           s.indicative_fte / NULLIF(frac_fte.denom,0), con.work_hours, con.hol_hours)
      ELSE s.indicative_FTE END as FTE
FROM input_pay_staff s
INNER JOIN f_set fs ON fs.set_id = s.set_id
LEFT OUTER JOIN (SELECT set_id, SUM(ISNULL(s.teaching_hours, 0)) as hours FROM input_pay_staff s WHERE s.post_type_id <> 'FRAC' GROUP BY set_id)
	as taught ON taught.set_id = s.set_id
LEFT OUTER JOIN (SELECT set_id, SUM(s.indicative_FTE) as denom FROM input_pay_staff s WHERE s.post_type_id = 'FRAC' AND s.indicative_fte IS NOT NULL GROUP BY set_id)
	as frac_fte on frac_fte.set_id = s.set_id
INNER JOIN staff_con_type  con ON con.con_type_id = s.con_type_id
         """
                ),
              o("v_calc_staff_monthly", f"""
SELECT s.staff_line_id, s.post_status_id, s.set_id, f_set.acad_year, f_set.set_cat_id, ISNULL(s.staff_id, s.staff_line_id) as staff_id,
{staff_month_sal}
FROM input_pay_staff s
INNER JOIN f_set ON f_set.set_id = s.set_id
INNER JOIN staff_spine ss on ss.spine = s.current_spine
INNER JOIN v_calc_staff_fte vFTE on vFTE.staff_line_id = s.staff_line_id
"""),
              o("v_calc_staff_monthly_total", f"""
SELECT m.staff_id, m.acad_year, m.set_cat_id,
{staff_month_sal_total}
FROM v_calc_staff_monthly m
LEFT OUTER JOIN staff_post_status ps ON ps.post_status_id = m.post_status_id
WHERE ps.exclude_from_finance = 0
GROUP BY m.staff_id, m.acad_year, m.set_cat_id
         """),
              o("v_calc_staff_monthly_all", f"""
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

              ]
