from finance_manager.functions import periods
from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views import account_description, _generate_p_string, _sql_bound


sql = """
SELECT 
  c.directorate_id, CAST(f.summary_code AS INT) as summary_code, s.acad_year, s.set_cat_id,  
  STUFF((
    SELECT '; ' + x.costc + ' - ' + x.notes 
    FROM 
	(
	SELECT f.notes, f.summary_code, s.costc, s.acad_year, s.set_cat_id, c.directorate_id
	FROM input_forecast f
	INNER JOIN f_set s on f.set_id = s.set_id
	INNER JOIN fs_cost_centre c ON c.costc = s.costc 
	) x 
    WHERE (directorate_id = c.directorate_id 
			AND summarY_code = f.summary_code 
			AND acad_year = s.acad_year
			AND set_cat_id = s.set_cat_id) 
    FOR XML PATH(''),TYPE).value('(./text())[1]','VARCHAR(MAX)')
  ,1,2,'') AS ConcatNotes
FROM input_forecast f
INNER JOIN f_set s on f.set_id = s.set_id
INNER JOIN fs_cost_centre c ON c.costc = s.costc 
WHERE len(f.notes) > 0 AND s.surpress = 0
GROUP BY 
c.directorate_id, f.summary_code, s.acad_year, s.set_cat_id
"""


def _view():
    view = o("v_luminate_notes", sql)
    return view
