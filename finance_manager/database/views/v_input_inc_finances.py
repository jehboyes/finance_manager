from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views import p_sum_string


def _view():
    view = o("v_input_inc_courses", f"""
SELECT *, {p_sum_string} as total
FROM input_inc_courses
    """)
    return view
