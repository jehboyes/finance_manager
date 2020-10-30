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
# for a period table
values_clause = ", ".join([f"({n})" for n in periods()])

# finance ui pivot
headers = ''

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
staff_total_pay = "+".join([f"a.p{n}" for n in periods()])
staff_total_ni = "+".join([f"a.ni_p{n}" for n in periods()])
staff_total_pension = "+".join([f"a.pension_p{n}" for n in periods()])

# Unpivot view strings
ucase_p_list = ", ".join([f"P{n}" for n in periods()])
staff_unpivot_ni = ", ".join([f"ni_p{n} as P{n}" for n in periods()])
staff_unpivot_pension = ", ".join([f"pension_p{n} as P{n}" for n in periods()])
staff_unpivot_core = """
SELECT staff_line_id, period, {col_header}
FROM 
    (SELECT staff_line_id, {periods}
        FROM v_calc_staff_monthly_all) p
UNPIVOT 
    ({col_header} for period in ("""+ucase_p_list + """)) as unp
"""

views = [o("v_input_pay_fracclaim", f"""
SELECT fs.set_id, ISNULL(fc.hours, 0) as hours, p.period 
FROM f_set fs 
CROSS JOIN 
(SELECT * FROM 
	(VALUES {values_clause}) AS X(period)) as p
LEFT OUTER JOIN input_pay_fracclaim fc ON fc.set_id = fs.set_id AND fc.period = p.period
"""), o("v_mri_finance", f"""
SELECT f.account, ISNULL(f.amount,0) as amount, e.coefficient,f.period, s.costc, s.acad_year, 
	scode.description as summary_code, sec.description as sec, sec.position as sec_order, 
	scode.position as line_order, 
	sc.description, fi.instance_id, s.set_id, 
	cast(s.acad_year as varchar) + ' ' + sc.set_cat_id as finance_summary 
FROM f_finance_instance fi 
CROSS JOIN fs_account a
INNER JOIN fs_entry_type e on a.default_balance = e.balance_type
LEFT JOIN f_finance f ON fi.instance_id = f.instance_id AND f.account = a.account
INNER JOIN f_set s ON fi.set_id = s.set_id
INNER JOIN f_set_cat sc ON s.set_cat_id = sc.set_cat_id 
INNER JOIN fs_summary_code scode ON  scode.summary_code = a.summary_code
INNER JOIN fs_section sec ON scode.section_id = sec.section_id
INNER JOIN 
	(SELECT max(instance_id) as instance_id, set_id FROM f_finance_instance GROUP BY set_id)
	as most_recent on most_recent.instance_id = fi.instance_id
"""),
    o("v_mri_finance_grouped_subtotal", f"""
SELECT set_id, acad_year, costc, sec, summary_code, sec_order, line_order, finance_summary, format = 'body',
	SUM(amount) as amount 
FROM v_mri_finance
GROUP BY set_id, acad_year, costc, sec, summary_code, sec_order, line_order, finance_summary
UNION ALL 
-- Section headers
SELECT set_id, acad_year, costc, sec,NULL as summary_code, sec_order, MIN(line_order)-1, 
	finance_summary, format = 'header', NULL as amount 
FROM v_mri_finance
GROUP BY set_id, acad_year, costc, sec, sec_order, finance_summary
UNION ALL
-- Subtotals
SELECT set_id, acad_year, costc, sec,'Subtotal' as summary_code, sec_order, MAX(line_order)+1, 
	finance_summary, format = 'subtotal', SUM(amount) as amount 
FROM v_mri_finance
GROUP BY set_id, acad_year, costc, sec, sec_order, finance_summary
UNION ALL
--Grand total
SELECT set_id, acad_year, costc, 'Summary' as sec,'Total' as summary_code, MAX(sec_order)+1, 
	MAX(line_order)+1, finance_summary, format = 'total', SUM(amount*coefficient)*-1 as amount 
FROM v_mri_finance
GROUP BY set_id, acad_year, costc, finance_summary
    """), o("v_ui_finance", f"""
SELECT costc, sec, summary_code, sec_order, line_order, format, [2020 BP3] as a
FROM (SELECT costc, sec, summary_code, sec_order, line_order, finance_summary, format, SUM(amount) as amount 
FROM [v_mri_finance_grouped_subtotal] GROUP BY costc, sec, summary_code, sec_order, line_order, finance_summary, format) p 
PIVOT
(SUM(amount) FOR finance_summary in ([2020 BP3])) as pvt    
    """), o("v_input_inc_courses", f"""
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
    o("v_calc_staff_tabulated", f"""
SELECT sal.*, ni.ni, pen.pension 
FROM 
(""" + staff_unpivot_core.format(col_header="salary", periods=ucase_p_list) + """) as sal
INNER JOIN 
(""" + staff_unpivot_core.format(col_header="ni", periods=staff_unpivot_ni) + """) as ni 
    ON ni.period = sal.period AND ni.staff_line_id = sal.staff_line_id
INNER JOIN 
(""" + staff_unpivot_core.format(col_header="pension", periods=staff_unpivot_pension) + """) as pen 
    ON pen.period = sal.period AND pen.staff_line_id = sal.staff_line_id"""
      ), o("v_input_pay_staff", f"""
SELECT s.*, 
{staff_total_pay} as pay_total,
{staff_total_ni} as ni_total,
{staff_total_pension} as pension_total
FROM input_pay_staff AS s
LEFT OUTER JOIN v_calc_staff_monthly_all a ON a.staff_line_id = s.staff_line_id
""")
]
