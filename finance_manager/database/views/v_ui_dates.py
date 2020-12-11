from finance_manager.database.replaceable import ReplaceableObject as o


def _view():
    sql = """
    SELECT d.set_cat_id, d.acad_year, d.dt, s.description + ' ' + c.description + ISNULL(' - ' + d.description,'') as description, 
	c.important
	FROM a_dt as d
	INNER JOIN a_dt_cat AS c on c.dt_cat_id = d.dt_cat_id
	INNER JOIN f_set_cat AS s ON s.set_cat_id = d.set_cat_id """
    return o("v_ui_dates", sql)
