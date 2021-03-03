"""View for reporting using the student-friendly categorisation."""
from finance_manager.database.replaceable import ReplaceableObject as o


sql = f"""
SELECT v.*, s.acad_year, s.costc, CAST(s.acad_year as CHAR(4)) + ' ' + s.set_cat_id as finance_summary, 
    CASE x.n WHEN 1 THEN c.directorate_id ELSE 'Z' END as directorate_id, --Creates a directorate Z copy of each line
    s.costc + ' ' + c.description as costc_description
FROM v_mri_finance_grouped_subtotal v
INNER JOIN f_set s ON v.set_id = s.set_id 
INNER JOIN fs_cost_centre c on c.costc = s.costc
CROSS JOIN (SELECT * FROM (VALUES (1), (2)) x(n)) as x 
WHERE s.surpress = 0  

UNION ALL

SELECT v.set_id, v.summary_code, v.summary, v.subsection, v.section, v.supersection, v.summary_order, v.sub_order,
	v.sec_order, v.super_order,
	-v.amount as amount, v.level, v.id, -v.intuitive_amount,
    s.acad_year, s.costc, CAST(s.acad_year as CHAR(4)) + ' ' + s.set_cat_id as finance_summary, 'Z' as directorate_id,
    s.costc + ' ' + c.description as costc_description
FROM v_mri_finance_grouped_subtotal_internal v
INNER JOIN f_set s ON v.set_id = s.set_id
INNER JOIN fs_cost_centre c on c.costc = s.costc
"""


def _view():
    return o("v_luminate_finance", sql)
