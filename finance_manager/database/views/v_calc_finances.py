"""
Defines a view that combines all of the input tables to produce a candidate finance set. 

NB- the curriculum database is referenced, and so to execute the view a user must have SELECT permission
on any referenced objects. 
"""
from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views import _generate_p_string
from finance_manager.functions import periods
jstr = ", "
# comma joined list of periods
cj_periods = _generate_p_string("({p})", jstr)
# mapping period column to number for pivot
ptext_as_n = _generate_p_string("p{p} as [{p}]", jstr)
square_list = _generate_p_string("[{p}]", jstr)

claim_case = _generate_p_string(
    "CASE x.n WHEN 1 THEN p{p}*adjusted_rate WHEN 2 THEN ni_p{p} ELSE pension_p{p} END as [{p}]", ",\n")

union_parts = "\nUNION ALL\n".join([f"""
--FEE BURSARIES (not the higher fee proportional one)
SELECT v.set_id, CASE WHEN v.status = 'H' THEN 1240 ELSE 1246 END as account, p.period, SUM(-amount * number)/12 as value
FROM v_input_inc_bursary v
CROSS JOIN (SELECT * FROM (VALUES {cj_periods}) as x(period)) as p
GROUP BY p.period, v.set_id, v.status
""", f"""
--OTHER COURSES
SELECT set_id, 1211 as account, period, value
FROM (SELECT set_id, {ptext_as_n}
		FROM v_input_inc_courses) p
UNPIVOT
(value for period in ({square_list})) as unp
""", f"""
--HE FEE (partially from the curriculummodel database)
SELECT s.set_id, case WHEN [fee status] = 'H' THEN 1240 ELSE 1246 END as account, p.period, income/12 as value FROM
curriculummodel.dbo.vfeeincomeinputcostc f
INNER JOIN f_set s ON s.acad_year = f.year AND s.costc = f.costc AND f.usage_id = s.student_number_usage_id
CROSS JOIN (SELECT * FROM (VALUES {cj_periods}) as X(period)) p
INNER JOIN f_set_cat fsc ON fsc.set_cat_id = s.set_cat_id 
WHERE fsc.is_forecast = 0 AND s.surpress = 0
""", f"""
--OfS HIGH COST AND CAPITAL GRANT 
SELECT s.set_id, 1100 as account, p.period, f.students/t.students*(g.capital_grant+g.high_cost_funding)/12 as value FROM
curriculummodel.dbo.vfeeincomeinputcostc f
INNER JOIN (SELECT year, usage_id, SUM(Students) as students
			FROM curriculummodel.dbo.vfeeincomeinputcostc
			GROUP BY year, usage_id) as t ON f.usage_id = t.usage_id AND t.year = f.Year
INNER JOIN f_set s ON s.acad_year = f.year AND s.costc = f.costc AND f.usage_id = s.student_number_usage_id
INNER JOIN input_inc_grant g ON s.acad_year = g.acad_year AND s.set_cat_id = g.set_cat_id
CROSS JOIN (SELECT * FROM (VALUES {cj_periods}) as X(period)) p
INNER JOIN f_set_cat fsc ON fsc.set_cat_id = s.set_cat_id 
WHERE fsc.is_forecast = 0 AND s.surpress = 0
""", f"""
--HE FEE WITHDRAWAL
SELECT s.set_id, CASE loss.status WHEN 'H' THEN 1900 ELSE 1901 END as account, p.period, -income/12.0*loss.rate as value FROM
curriculummodel.dbo.vfeeincomeinputcostc f
INNER JOIN f_set s ON s.acad_year = f.year AND s.costc = f.costc AND f.usage_id = s.student_number_usage_id
INNER JOIN v_input_inc_feeloss loss ON s.set_id = loss.set_id AND f.[Fee Status] = loss.status
CROSS JOIN (SELECT * FROM (VALUES {cj_periods}) as X(period)) p
INNER JOIN f_set_cat fsc ON fsc.set_cat_id = s.set_cat_id 
WHERE fsc.is_forecast = 0 AND s.surpress = 0
""", f"""
--HIGHER FEE BURSARY (moving a proportion of student income to Access & Participation)
--Cross join the income rom student numbers 
SELECT CASE a.account WHEN 4370 THEN s.set_id ELSE app.set_id END as set_id,
a.account as account, p.period, ROUND(income/12.0*(1-loss.rate)*b.hfi_prop*b.bursary_prop,2) as value
FROM curriculummodel.dbo.vfeeincomeinputcostc f
INNER JOIN f_set s ON s.acad_year = f.year AND s.costc = f.costc AND f.usage_id = s.student_number_usage_id
INNER JOIN v_input_inc_feeloss loss ON s.set_id = loss.set_id AND f.[Fee Status] = loss.status
INNER JOIN conf_hfi_bursary b ON b.acad_year = s.acad_year AND b.set_cat_id = s.set_cat_id
INNER JOIN f_set app ON app.acad_year = s.acad_year AND app.set_cat_id = s.set_cat_id AND app.costc = 'MA1420'
CROSS JOIN (SELECT * FROM (VALUES {cj_periods}) as X(period)) p
CROSS JOIN (SELECT * FROM (VALUES (4370), (4360)) as X(account)) a
INNER JOIN f_set_cat fsc ON fsc.set_cat_id = s.set_cat_id 
WHERE fsc.is_forecast = 0 AND s.costc <> 'MC1610' AND s.surpress = 0
""", f"""
--OTHER INCOME
SELECT set_id, account, period, value FROM
(SELECT set_id, account, {ptext_as_n} FROM v_input_inc_other WHERE account is NOT NULL) p
UNPIVOT (value for period in ({square_list})) unp
""", f"""
--INTERNAL NON PAY
SELECT set_id, account, period, CASE net WHEN 0 THEN amount/12 ELSE 0 END as value
FROM v_input_nonp_internal
CROSS JOIN (SELECT * FROM (VALUES {cj_periods}) as x(period)) p
""", f"""
--EXTERNAL NON PAY
SELECT set_id, account, period, value FROM
(SELECT set_id, account, {ptext_as_n} FROM v_input_nonp_other WHERE account is not null) p
UNPIVOT (value for period in ({square_list})) unp
""", f"""
--CLAIMS
SELECT set_id, account, period, value FROM
(SELECT c.set_id, 
		CASE x.n 
			WHEN 1 THEN c.account 
			WHEN 2 THEN CASE c.account 
							WHEN 2102 THEN 2418 
				 			ELSE c.account END
			ELSE CASE c.account 
					WHEN 2102 THEN 2518 
					ELSE c.account 
					END 
			END as account, 
		{claim_case}  
	FROM v_calc_claim c
	CROSS JOIN (SELECT * FROM (VALUES (1), (2), (3)) as x(n)) x) as p --Used to split pension
UNPIVOT (value FOR period IN ({square_list})) unp
""", f"""
--Moving frac contracts to frac claims
SELECT
fs.set_id,
CASE WHEN p.period = 0 THEN 2100 WHEN x.n = 1 THEN pt.salary_account WHEN x.n = 2 then pt.ni_account ELSE pt.pension_account END as account,
CASE WHEN p.period = 0 THEN f.period ELSE p.period END as period,
CASE WHEN p.period = 0 THEN 1 ELSE -1/12.0 END * CASE fs.curriculum_hours WHEN 0 then 0 ELSE f.hours/fs.curriculum_hours END*CASE WHEN x.n = 1 THEN v.salary WHEN x.n = 2 then v.ni ELSE v.pension END as value
FROM input_pay_fracclaim f
INNER JOIN f_set fs ON fs.set_id = f.set_id
INNER JOIN (SELECT s.set_id, s.post_type_id, SUM(salary) as salary, SUM(NI) as ni, SUM(pension) as pension
			FROM v_calc_staff_tabulated t
			INNER JOIN input_pay_staff s ON t.staff_line_id = s.staff_line_id
			WHERE s.post_type_id = 'FRAC'
			GROUP BY s.set_id, s.post_type_id) AS v ON v.set_id = f.set_id
INNER JOIN staff_post_type pt ON pt.post_type_id = v.post_type_id
CROSS JOIN (SELECT * FROM (VALUES (0), (1), (2), (3), (4), (5), (6), (7), (8), (9), (10), (11), (12)) as x(period)) p
CROSS JOIN (SELECT * FROM (VALUES (1), (2), (3)) as x(n)) x --This is correct: split each fracclaim period
WHERE f.hours > 0
""", f"""
--STAFFING
SELECT s.set_id, 
case 
WHEN x.n = 1 then p.salary_account 
WHEN x.n = 2 THEN p.ni_account 
WHEN x.n = 3 THEN p.pension_account 
ELSE 2301 END as account,
SUBSTRING(t.period, 2,2) as period ,
case 
WHEN x.n=1 then t.salary 
WHEN x.n=2 then t.ni 
WHEN x.n=3 then t.pension 
ELSE t.travel END AS value
FROM v_calc_staff_tabulated t
INNER JOIN input_pay_staff s ON s.staff_line_id = t.staff_line_id
INNER JOIN staff_post_type p ON p.post_type_id = s.post_type_id
CROSS JOIN (SELECT * FROM (VALUES (1), (2), (3), (4)) as x(n)) x

""", f"""
--FORECAST
SELECT v.set_id, v.account, v.period, v.amount 
FROM (
	--First the actuals
	SELECT x.set_id, af.account, af.period, af.amount 
	FROM conf_forecast c 
	INNER JOIN f_set x ON x.set_cat_id = c.set_cat_id
						AND x.acad_year = c.acad_year 
	INNER JOIN f_set a ON a.acad_year = c.acad_year
							AND a.set_cat_id = c.comp_set_cat_main
							AND a.costc = x.costc
	INNER JOIN v_mri_finance af ON af.set_id = a.set_id
	WHERE af.period <= c.split_at_period
	UNION ALL
	--And the forecasted component 
	SELECT f.set_id, sc.default_account as account, p.period, f.amount/(12-c.split_at_period) as amount 
	FROM input_forecast f
	INNER JOIN f_set s ON s.set_id = f.set_id 
	INNER JOIN conf_forecast c ON c.set_cat_id = s.set_cat_id AND c.acad_year = s.acad_year  
	CROSS JOIN (SELECT * FROM (VALUES {cj_periods}) as x(period)) as p
	INNER JOIN fs_summary_code sc ON f.summary_code = sc.summary_code 
	WHERE p.period > c.split_at_period
) v
INNER JOIN f_set s ON s.set_id = v.set_id 
INNER JOIN f_set_cat fsc ON fsc.set_cat_id = s.set_cat_id
WHERE fsc.is_forecast = 1

""", f"""
--CAPEX
--Overrides the set to general overheads (in the same cat/year). 
SELECT p.set_id, 4900 as account, 1 as period, v.total_amount/4 
FROM v_input_capex v 
INNER JOIN f_set f ON v.set_Id = f.set_id
INNER JOIN f_set p ON p.set_cat_id = f.set_cat_id AND p.acad_year = f.acad_year AND p.costc = 'MA1300'
"""])


def _view():
    view = o("v_calc_finances", f"""
	SELECT x.set_id, x.account, x.period, ROUND(SUM(x.value),2) as amount FROM ({union_parts}) as x
	INNER JOIN f_set s ON s.set_id = x.set_id 
	WHERE value <> 0 AND account is not NULL AND s.surpress = 0
	GROUP BY x.set_id, x.account, x.period
	""")
    return view
