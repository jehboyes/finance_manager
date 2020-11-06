from finance_manager.database.replaceable import ReplaceableObject as o


view = o("v_mri_finance", f"""
SELECT a.account, ISNULL(f.amount,0) as amount, e.coefficient,f.period, s.costc, s.acad_year, 
    scode.summary_code as sc_id, cc.directorate_id, 
	scode.description as summary_code, sec.description as sec, sec.position as sec_order, 
	scode.position as line_order, 
	sc.description, fi.instance_id, s.set_id, a.hide_from_users, a.description as account_description, 
	cast(s.acad_year as varchar) + ' ' + sc.set_cat_id as finance_summary 
FROM f_finance_instance fi 
CROSS JOIN fs_account a
INNER JOIN fs_entry_type e on a.default_balance = e.balance_type
LEFT JOIN f_finance f ON fi.instance_id = f.instance_id AND f.account = a.account
INNER JOIN f_set s ON fi.set_id = s.set_id
INNER JOIN f_set_cat sc ON s.set_cat_id = sc.set_cat_id 
INNER JOIN fs_summary_code scode ON  scode.summary_code = a.summary_code
INNER JOIN fs_section sec ON scode.section_id = sec.section_id
INNER JOIN fs_cost_centre cc ON cc.costc = s.costc
INNER JOIN 
	(SELECT max(instance_id) as instance_id, set_id FROM f_finance_instance GROUP BY set_id)
	as most_recent on most_recent.instance_id = fi.instance_id
""")