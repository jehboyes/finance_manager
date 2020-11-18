from finance_manager.database.replaceable import ReplaceableObject as o


def _view():
    sql = """
    SELECT DISTINCT c.costc, c.description as costc_name, c.costc+' '+c.description as long_name, 
s.set_id, s.acad_year, s.curriculum_id, sc.description as code, lower(core.login_365) as login_365, 
	CAST(s.acad_year as varchar) + ' ' + sc.description as year_code, s.closed
FROM 
	(SELECT costc, owner as login_365 FROM fs_cost_centre
	 UNION ALL 
	 SELECT costc, login_365 FROM a_permission
	 UNION ALL 
	 SELECT c.costc, d.director 
	 FROM fs_directorate d INNER JOIN fs_cost_centre c ON c.directorate_id = d.directorate_id
	 ) as core
INNER JOIN fs_cost_centre c ON core.costc = c.costc 
INNER JOIN f_set s ON core.costc = s.costc 
INNER JOIN f_set_cat sc ON sc.set_cat_id = s.set_cat_id"""
    return o("v_ui_permissions", sql)
