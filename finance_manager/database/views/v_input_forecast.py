"""
View for inputting forecast in UI.
"""
from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views import get_headers
from finance_manager.database.views.v_calc_forecast import _view as calc_view


def _view():
    calc_headers = get_headers(calc_view().sqltext)
    calc_headers = [f"f.{h}" for h in calc_headers]
    agg_headers = []
    for head in calc_headers:
        if "set_id" in head:
            agg_headers.append(head)
        elif "summary_code" in head or "notes":
            agg_headers.append("NULL")
        else:
            agg_headers.append(f"SUM({head})")
    source = """FROM v_calc_forecast f
	INNER JOIN fs_summary_code sc on f.summary_code = sc.summary_code
	INNER JOIN fs_sub_section ss ON ss.sub_section_id = sc.sub_section_id
	INNER JOIN fs_section s ON s.section_id = ss.section_id
	"""
    sql = f"""
	SELECT {", ".join(calc_headers)}, 
		sc.position as summary_order, s.position as section_order, 
		sc.description as summary, NULL as section
	{source}
	UNION ALL
	SELECT {", ".join(agg_headers)}, 
		MAX(sc.position)+1, s.position, 
		NULL, s.description
	{source}
	GROUP BY s.position, s.description, f.set_id	
	"""
    view = o("v_input_forecast", sql)
    return view
