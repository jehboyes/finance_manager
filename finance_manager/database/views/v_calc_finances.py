""" 
Module for the finance view. 
"""
from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.functions import periods
jstr = ", \n"
cj_periods = jstr.join([f"({n})" for n in periods()])
ptext_as_n = jstr.join([f"p{n} as [{n}]" for n in periods()])
square_list = jstr.join([f"[{n}]" for n in periods()])
ni_bit = jstr.join(
    [f"c.p{n}*r.rate*x.a+(c.p{n}*r.rate-n.p{n})*n.rate*x.b as [{n}]" for n in periods()])


union_parts = f"""
--BURSARIES
SELECT v.set_id, CASE WHEN v.status = 'H' THEN 1240 ELSE 1246 END as account, p.period, SUM(-amount * number)/12 as value
FROM v_input_inc_bursary v
CROSS JOIN (SELECT * FROM (VALUES {cj_periods}) as x(period)) as p
GROUP BY p.period, v.set_id, v.status
UNION ALL 
--OTHER COURSES
SELECT set_id, 1211 as account, period, value
FROM (SELECT set_id, {ptext_as_n}
		FROM v_input_inc_courses) p 
UNPIVOT
(value for period in ({square_list})) as unp
UNION ALL
--HE FEE
SELECT s.set_id, case WHEN [fee status] = 'H' THEN 1240 ELSE 1246 END as account, p.period, income/12 as value FROM 
curriculummodel.dbo.vfeeincomeinputcostc f 
INNER JOIN f_set s ON s.acad_year = f.year AND s.costc = f.costc AND f.usage_id = s.student_number_usage_id
CROSS JOIN (SELECT * FROM (VALUES {cj_periods}) as X(period)) p
UNION ALL
--HE FEE WITHDRAWAL
SELECT s.set_id, 1900 as account, p.period, -income/12.0*loss.rate as value FROM 
curriculummodel.dbo.vfeeincomeinputcostc f 
INNER JOIN f_set s ON s.acad_year = f.year AND s.costc = f.costc AND f.usage_id = s.student_number_usage_id
INNER JOIN v_input_inc_feeloss loss ON s.set_id = loss.set_id AND f.[Fee Status] = loss.status
CROSS JOIN (SELECT * FROM (VALUES {cj_periods}) as X(period)) p
UNION ALL 
--OTHER INCOME
SELECT set_id, account, period, value FROM 
(SELECT set_id, account, {ptext_as_n} FROM v_input_inc_other WHERE account is null) p 
UNPIVOT (value for period in ({square_list})) unp
UNION ALL 
--INTERNAL NON PAY 
SELECT set_id, account, period, amount/12 as value 
FROM v_input_nonp_internal 
CROSS JOIN (SELECT * FROM (VALUES {cj_periods}) as x(period)) p
UNION ALL
--EXTERNAL NON PAY
SELECT set_id, account, period, value FROM
(SELECT set_id, account, {ptext_as_n} FROM v_input_nonp_other WHERE account is not null) p
UNPIVOT (value for period in ({square_list})) unp
UNION ALL 
--CLAIMS. Cross join used to work out NI at same time
SELECT * FROM 
(SELECT c.set_id, CASE WHEN x.a=1 THEN c.account ELSE 2418 END as account, 
	{ni_bit}
	FROM input_pay_claim c
	INNER JOIN f_set s ON s.set_id = c.set_id 
	INNER JOIN (SELECT claim_id, (isnull(rate,0)*variable_rate+rate_uplift)*base_multiplier*holiday_multiplier as rate
				FROM input_pay_claim a INNER JOIN input_pay_claim_type b ON a.claim_type_id = b.claim_type_id) 
			as r on r.claim_id = c.claim_id
	INNER JOIN staff_ni n ON n.acad_year = s.acad_year
	CROSS JOIN (SELECT * FROM (VALUES (0,1), (1,0)) AS x(a,b)) as x) as p
UNPIVOT (value FOR period IN ({square_list})) unp
UNION ALL 
--Moving frac contracts to frac claims
SELECT 
fs.set_id, 
CASE WHEN p.period = 0 THEN 2102 WHEN x.n = 1 THEN pt.salary_account WHEN x.n = 2 then pt.ni_account ELSE pt.pension_account END as account, 
CASE WHEN p.period = 0 THEN f.period ELSE p.period END as period, 
CASE WHEN p.period = 0 THEN 1 ELSE -1/12.0 END * f.hours/fs.curriculum_hours*CASE WHEN x.n = 1 THEN v.salary WHEN x.n = 2 then v.ni ELSE v.pension END as value
FROM input_pay_fracclaim f 
INNER JOIN f_set fs ON fs.set_id = f.set_id 
INNER JOIN (SELECT s.set_id, s.post_type_id, SUM(salary) as salary, SUM(NI) as ni, SUM(pension) as pension 
			FROM v_calc_staff_tabulated t 
			INNER JOIN input_pay_staff s ON t.staff_line_id = s.staff_line_id
			WHERE s.post_type_id = 'FRAC'
			GROUP BY s.set_id, s.post_type_id) AS v ON v.set_id = f.set_id 
INNER JOIN staff_post_type pt ON pt.post_type_id = v.post_type_id
CROSS JOIN (SELECT * FROM (VALUES (0), (1), (2), (3), (4), (5), (6), (7), (8), (9), (10), (11), (12)) as x(period)) p
CROSS JOIN (SELECT * FROM (VALUES (1), (2), (3)) as x(n)) x
WHERE f.hours > 0
UNION ALL
--STAFFING
SELECT s.set_id, case WHEN x.n = 1 then p.salary_account WHEN x.n = 2 THEN p.ni_account ELSE p.pension_account END as account, 
SUBSTRING(t.period, 2,2) as period , 
case WHEN x.n=1 then t.salary WHEN x.n=2 then t.ni ELSE t.pension END AS value
FROM v_calc_staff_tabulated t
INNER JOIN input_pay_staff s ON s.staff_line_id = t.staff_line_id 
INNER JOIN staff_post_type p ON p.post_type_id = s.post_type_id
CROSS JOIN (SELECT * FROM (VALUES (1), (2), (3)) as x(n)) x	
"""

view = o("v_calc_finances", f"""
SELECT set_id, account, period, ROUND(SUM(value),2) as value FROM ({union_parts}) as x
WHERE value > 0 AND account is not NULL
GROUP BY set_id, account, period 
""")
