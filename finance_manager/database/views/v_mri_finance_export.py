from finance_manager.database.replaceable import ReplaceableObject as o


def _view():
    sql = """
	SELECT s.set_cat_id, f.acad_year, f.costc, ISNULL(m.t, f.account) as account, f.period, 
        ROUND(SUM(f.amount*f.coefficient),2) as amount, CASE f.costc WHEN 'MZ1000' THEN 1 ELSE 0 END as governors
    FROM v_mri_finance f  
    INNER JOIN f_set s ON s.set_id = f.set_id
    LEFT JOIN (SELECT * FROM (VALUES (1900, 1240), (1901, 1245)) x(f, t)) as m ON m.f=f.account
	WHERE f.amount <> 0
	GROUP BY s.set_cat_id, f.acad_year, f.costc, m.t, f.account, f.period
    """
    return o("v_mri_finance_export", sql)
