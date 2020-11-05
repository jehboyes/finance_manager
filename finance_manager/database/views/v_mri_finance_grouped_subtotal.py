from finance_manager.database.replaceable import ReplaceableObject as o

view = o("v_mri_finance_grouped_subtotal", f"""
SELECT set_id, acad_year, costc, sec, summary_code, sc_id, sec_order, line_order, finance_summary, format = 'body',
	SUM(amount) as amount 
FROM v_mri_finance
GROUP BY set_id, acad_year, costc, sec, summary_code, sc_id, sec_order, line_order, finance_summary
UNION ALL 
-- Section headers
SELECT set_id, acad_year, costc, sec,NULL as summary_code, NULL, sec_order, MIN(line_order)-1, 
	finance_summary, format = 'header', NULL as amount 
FROM v_mri_finance
GROUP BY set_id, acad_year, costc, sec, sec_order, finance_summary
UNION ALL
-- Subtotals
SELECT set_id, acad_year, costc, sec,'Subtotal' as summary_code, NULL, sec_order, MAX(line_order)+1, 
	finance_summary, format = 'subtotal', SUM(amount) as amount 
FROM v_mri_finance
GROUP BY set_id, acad_year, costc, sec, sec_order, finance_summary
UNION ALL
--Grand total
SELECT set_id, acad_year, costc, 'Summary' as sec,'Total' as summary_code, NULL as sc_id, MAX(sec_order)+1, 
	MAX(line_order)+1, finance_summary, format = 'total', SUM(amount*coefficient)*-1 as amount 
FROM v_mri_finance
GROUP BY set_id, acad_year, costc, finance_summary
    """)
