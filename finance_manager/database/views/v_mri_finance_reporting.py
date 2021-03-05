"""View for reporting using the student-friendly categorisation."""
from finance_manager.database.replaceable import ReplaceableObject as o


sql = f"""
SELECT f.acad_year, 
    s.set_cat_id, 
    ra.description as rep_a, 
    rb.description as rep_b, 
    cc.costc, 
    f.account, 
    cc.directorate_id,
    s4.description as super_section, 
    CASE s4.super_section_id WHEN 'I' THEN 'Income' ELSE 'Expenditure' END as i_or_e,
	SUM(f.amount) as amount, SUM(f.amount * -1 * e.coefficient) as intuitive_amount 
FROM v_mri_finance f
INNER JOIN f_set s ON f.set_id = s.set_id 
INNER JOIN fs_cost_centre cc ON cc.costc = s.costc
INNER JOIN fs_account a ON a.account = f.account 
INNER JOIN fs_entry_type e ON e.balance_type = a.default_balance
INNER JOIN fs_reporting_cat_config c ON c.costc = f.costc and c.account = a.account 
INNER JOIN fs_reporting_cat_a ra ON ra.rep_cat_a_id = c.rep_cat_a_id 
INNER JOIN fs_reporting_cat_b rb ON rb.rep_cat_b_id = ra.rep_cat_b_id 
INNER JOIN fs_summary_code s1 ON s1.summary_code = a.summary_code
INNER JOIN fs_sub_section s2 ON s2.sub_section_id = s1.sub_section_id
INNER JOIN fs_section s3 ON s3.section_id = s2.section_id
INNER JOIN fs_super_section s4 ON s4.super_section_id = s3.super_section_id
GROUP BY f.acad_year, f.account, ra.description, rb.description, cc.directorate_id, cc.costc, s4.description, 
    s.set_cat_id, s4.super_section_id  
HAVING SUM(f.amount) <> 0
"""


def _view():
    return o("v_mri_finance_reporting", sql)
