"""
Contains defintions for the more complex views, i.e. those which explicitly reference multiple period columns

Handy strings are at the top, then actual views are defined as replacable objects (in `views` list).
"""
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

# work out a line's monthly FTE
staff_month_sal = ", \n".join(
    [f"dbo.udfGetMonthProp(f_set.acad_year, {n}, s.start_date, s.end_date)*vFTE.FTE*(ss.value+s.allowances)/12 as p{n}"
     for n in periods()])
staff_month_sal_total = ", \n".join(
    [f"SUM(m.p{n}) as p{n}" for n in periods()])
staff_month_ni = ", \n".join(
    [f"dbo.udfNI(mt.p{n}, ni.p{n}, ni.rate)*m.p{n}/NULLIF(ISNULL(NULLIF(mt.p{n},0),m.p{n}),0) as ni_p{n}" for n in periods()])
staff_month_pension = ", \n".join(
    [f"m.p{n}*ISNULL(pension.p{n},0) as pension_p{n}" for n in periods()])
staff_travel_months = 9
staff_travel_allowance = ", \n ".join(
    [f"s.travel_scheme/{staff_travel_months} as travel_p{n}" for n in range(3, 3+staff_travel_months)])
staff_total_pay = "+".join([f"a.p{n}" for n in periods()])
staff_total_ni = "+".join([f"a.ni_p{n}" for n in periods()])
staff_total_pension = "+".join([f"a.pension_p{n}" for n in periods()])

views = [o("v_input_inc_other", f"""
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

         o("v_input_pay_claim", f"""
SELECT i.set_id, i.claim_id, i.account, i.description, {account_description}, i.rate,
t.description as claim_type, t.claim_type_id,
a.description as account_name,
{p_list_string}, {p_sum_string} as hours,
({p_sum_string})*(ISNULL(i.rate,0)*t.variable_rate+t.rate_uplift)*t.base_multiplier*t.holiday_multiplier as amount
FROM input_pay_claim i
LEFT OUTER JOIN input_pay_claim_type t ON i.claim_type_id = t.claim_type_id
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
                                         AND m.set_cat_id = m.set_cat_id
INNER JOIN input_pay_staff s ON s.staff_line_id = m.staff_line_id
LEFT OUTER JOIN staff_pension_contrib pension ON pension.pension_id = s.pension_id AND pension.acad_year = m.acad_year
INNER JOIN staff_ni ni ON ni.acad_year = m.acad_year 
"""),
         o("v_input_pay_staff", f"""
SELECT s.*, 
{staff_total_pay} as pay_total,
{staff_total_ni} as ni_total,
{staff_total_pension} as pension_total
FROM input_pay_staff AS s
LEFT OUTER JOIN v_calc_staff_monthly_all a ON a.staff_line_id = s.staff_line_id
""")
         ]
