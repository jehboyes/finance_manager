from finance_manager.database.replaceable import ReplaceableObject as o


source = """FROM v_mri_finance  f
LEFT OUTER JOIN fs_summary_code sc ON sc.summary_code = f.summary_code
LEFT OUTER JOIN fs_sub_section sub ON sub.sub_section_id = sc.sub_section_id
LEFT OUTER JOIN fs_section s ON s.section_id = sub.section_id 
LEFT OUTER JOIN fs_super_section super ON super.super_section_id = s.super_section_id
"""

sql = """
--Summary code
SELECT f.set_id, sc.summary_code, sc.description as summary, NULL as subsection, NULL as section, NULL as supersection,  
	MIN(sc.position) as summary_order,
	MIN(sub.line_order) as sub_order, 
	MIN(s.position) as sec_order, 
	MIN(super.position) as super_order, 
	SUM(f.amount) as amount, 'summary' as level, sc.summary_code as id,
	ROUND(SUM(f.amount*f.coefficient*-1),2) as intuitive_amount 
{source}
GROUP BY f.set_id, sc.summary_code, sc.description, sub.sub_section_id, s.section_id, super.super_section_id

UNION ALL
--SubSection
SELECT f.set_id, NULL, NULL, sub.description + ' Total' , NULL, NULL, 
	MAX(sc.position) +1 as summary_order,
	MIN(sub.line_order) as sub_order, 
	MIN(s.position) as sec_order, 
	MIN(super.position) as super_order, 
	SUM(f.amount) as amount, 'sub', sub.sub_section_id
	, ROUND(SUM(f.amount*f.coefficient*-1),2) as intuitive_amount
{source}
GROUP BY f.set_id, sub.description, sub.sub_section_id, s.section_id, super.super_section_id

UNION ALL
--Section Headers
SELECT f.set_id, NULL, NULL, NULL, s.description, NULL, 
	MIN(sc.position)-1 as summary_order,
	MIN(sub.line_order) as sub_order, 
	MIN(s.position) as sec_order, 
	MIN(super.position) as super_order, 
	NULL as amount, 'secheader', NULL
	, ROUND(SUM(f.amount*f.coefficient*-1),2) as intuitive_amount
{source}
GROUP BY f.set_id, s.description, s.section_id, super.super_section_id

UNION ALL
--Section 
SELECT f.set_id, NULL, NULL, NULL, s.description + ' Total', NULL, 
	MAX(sc.position) +1 as summary_order,
	MAX(sub.line_order) +1 as sub_order, 
	MIN(s.position) as sec_order, 
	MIN(super.position) as super_order, 
	SUM(f.amount) as amount, 'section', s.section_id 
	, ROUND(SUM(f.amount*f.coefficient*-1),2) as intuitive_amount
{source}
GROUP BY f.set_id, s.description, s.section_id, super.super_section_id

UNION ALL
--Super Section 
SELECT f.set_id, NULL, NULL, NULL, NULL, super.description + ' Total', 
	MAX(sc.position) +1 as summary_order,
	MAX(sub.line_order) +1 as sub_order, 
	MAX(s.position) +1 as sec_order, 
	MIN(super.position) as super_order, 
	SUM(f.amount) as amount, 'super', super.super_section_id, ROUND(SUM(f.amount*f.coefficient*-1),2) as intuitive_amount
{source}
GROUP BY f.set_id, super.description, super.super_section_id

UNION ALL 
--EBITDA Line
SELECT f.set_id, NULL, NULL, NULL, NULL, 'Luminate EBITDA', MAX(sc.position) +1, max(sub.line_order)+1, max(s.position) +2, 4, 
	SUM(f.amount * f.coefficient * -1) as amount, 'special', 'ebitda', ROUND(SUM(f.amount*f.coefficient*-1),2) as intuitive_amount
{source}
WHERE (super.super_section_id <> 'C' AND super.super_section_id <> 'E')
GROUP BY f.set_id

UNION ALL 
--Total Line
SELECT f.set_id, NULL, NULL, NULL, NULL, 'Net Surplus/(Deficit)', MAX(sc.position) +1, max(sub.line_order)+1, max(s.position), max(super.position)+1, 
	SUM(f.amount * f.coefficient * -1) as amount, 'special', 'total', ROUND(SUM(f.amount*f.coefficient*-1),2) as intuitive_amount
{source}
WHERE (super.super_section_id <> 'E')
GROUP BY f.set_id

UNION ALL 
--Grand total Line
SELECT f.set_id, NULL, NULL, NULL, NULL, 'Net Surplus/(Deficit)', MAX(sc.position) +1, max(sub.line_order)+1, max(s.position), max(super.position)+1, 
	SUM(f.amount * f.coefficient * -1) as amount, 'special', 'grand_total', ROUND(SUM(f.amount*f.coefficient*-1),2) as intuitive_amount
{source}
GROUP BY f.set_id

UNION ALL 
--Balanced recharge line
SELECT f.set_id, NULL, NULL, NULL, NULL, 'Net Recharge', MAX(sc.position) +1, max(sub.line_order)+1, max(s.position), max(super.position)+1, 
	SUM(f.amount * f.coefficient * -1) as amount, 'special', 'recharge', ROUND(SUM(f.amount*f.coefficient*-1),2) as intuitive_amount
{source}
WHERE (super.super_section_id = 'E')
GROUP BY f.set_id


UNION ALL 
--Total Expenditure
SELECT f.set_id, NULL, NULL, NULL, NULL, 'Total Expenditure', MAX(sc.position) +1, max(sub.line_order)+1, max(s.position) +1, 3, 
	SUM(f.amount) as amount, 'special', 'expenditure', ROUND(SUM(f.amount*f.coefficient*-1),2) as intuitive_amount
{source}
WHERE (super.super_section_id = 'P' OR  super.super_section_id = 'N')  
GROUP BY f.set_id


UNION ALL 
--EBELL
SELECT f.set_id, NULL, NULL, NULL, NULL, 'Earnings before Luminate & Leases', MAX(sc.position) +1, max(sub.line_order)+1, max(s.position) +2, 3, 
	SUM(f.amount* f.coefficient * -1) as amount, 'special', 'ebell', ROUND(SUM(f.amount*f.coefficient*-1),2) as intuitive_amount
{source}
WHERE (super.super_section_id = 'P' OR  super.super_section_id = 'N' OR super.super_section_id = 'I')  
GROUP BY f.set_id

"""


def _view():
    return o("v_mri_finance_grouped_subtotal", sql.format(source=source))
