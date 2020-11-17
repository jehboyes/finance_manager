from finance_manager.database.replaceable import ReplaceableObject as o


def _view():
    sql = f"""
SELECT fs.set_id, isnull(floss.rate,l.rate) as rate, s.status 
FROM f_set fs
CROSS JOIN 
(SELECT * FROM 
	(VALUES ('H'), ('O')) AS X(status)) as s
LEFT OUTER JOIN input_inc_feeloss floss 
	ON floss.set_id = fs.set_id AND s.status = floss.status
INNER JOIN conf_fee_loss l ON l.acad_year = fs.acad_year and l.set_cat_id = fs.set_cat_id and l.status = s.status
    """
    view = o("v_input_inc_feeloss", sql)
    return view
