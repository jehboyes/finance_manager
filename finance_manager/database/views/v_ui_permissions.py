from finance_manager.database.replaceable import ReplaceableObject as o


def _view():
    sql = """
    SELECT DISTINCT c.costc, c.description as costc_name, c.costc+' '+c.description as long_name, 
s.set_id, s.acad_year, s.curriculum_id, CAST(s.acad_year as varchar) + ' ' + sc.description as code, lower(core.login_365) as login_365, 
	CAST(s.acad_year as varchar) + ' ' + sc.description as year_code, s.closed, s.set_cat_id, 
	sc.is_forecast, comp_acad_year_a as prev_year, 
	conf_sca.description as prev_desc, 
	conf_scb.description as mri_desc, conf.split_at_period
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
INNER JOIN f_set_cat sc ON sc.set_cat_id = s.set_cat_id
LEFT OUTER JOIN conf_forecast conf ON conf.set_cat_id = sc.set_cat_id AND conf.acad_year = s.acad_year
LEFT OUTER JOIN f_set_cat conf_sca ON conf_sca.set_cat_id = conf.comp_set_cat_a
LEFT OUTER JOIN f_set_cat conf_scb ON conf_scb.set_cat_id = conf.comp_set_cat_b
LEFT OUTER JOIN conf_set_hide csh ON csh.set_cat_Id = s.set_cat_id AND csh.acad_year = s.acad_year
WHERE csh.set_cat_id IS NULL
"""
    return o("v_ui_permissions", sql)
