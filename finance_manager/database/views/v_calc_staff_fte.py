from finance_manager.database.replaceable import ReplaceableObject as o


def _view():
    view = o("v_calc_staff_fte", f"""
SELECT staff_line_id,
   CASE 
      WHEN s.post_type_id = 'FRAC' THEN
            dbo.udfFracFTE((fs.curriculum_hours-ISNULL(taught.hours,0)) *
                           s.indicative_fte / NULLIF(frac_fte.denom,0), con.work_hours, con.hol_hours)
      WHEN s.post_status_id = 'OLD' THEN 
            0 -- to reflect pre-change posts shouldn't have any impact 
      ELSE s.indicative_FTE END as FTE
FROM input_pay_staff s
INNER JOIN f_set fs ON fs.set_id = s.set_id
LEFT OUTER JOIN (SELECT set_id, SUM(ISNULL(s.teaching_hours, 0)) + 
                                    SUM(ISNULL(s.assessing_hours, 0)) + 
                                    SUM(ISNULL(s.coordination_hours, 0)) as hours                                
                    FROM input_pay_staff s WHERE s.post_type_id = 'CURM' GROUP BY set_id)
	as taught ON taught.set_id = s.set_id
LEFT OUTER JOIN (SELECT set_id, SUM(s.indicative_FTE) as denom FROM input_pay_staff s WHERE s.post_type_id = 'FRAC' AND s.indicative_fte IS NOT NULL GROUP BY set_id)
	as frac_fte on frac_fte.set_id = s.set_id
INNER JOIN staff_con_type  con ON con.con_type_id = s.con_type_id AND con.acad_year = fs.acad_year AND con.set_cat_id = fs.set_cat_id
         """
             )
    return view
