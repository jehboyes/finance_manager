from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.functions import periods

# Unpivot view strings
ucase_p_list = ", ".join([f"P{n}" for n in periods()])
staff_unpivot_ni = ", ".join([f"ni_p{n} as P{n}" for n in periods()])
staff_unpivot_pension = ", ".join([f"pension_p{n} as P{n}" for n in periods()])
staff_unpivot_travel = ", ".join([f"travel_p{n} as P{n}" for n in periods()])
staff_unpivot_spine = ", ".join([f"sp_p{n} as P{n}" for n in periods()])
staff_unpivot_core = """
SELECT staff_line_id, period, {col_header}
FROM 
    (SELECT staff_line_id, {periods}
        FROM v_calc_staff_monthly_all) p
UNPIVOT 
    ({col_header} for period in ("""+ucase_p_list + """)) as unp
"""

sql = f"""
SELECT sal.*, ni.ni, pen.pension, travel.travel, spine.sp
FROM 
(""" + staff_unpivot_core.format(col_header="salary", periods=ucase_p_list) + """) as sal
INNER JOIN 
(""" + staff_unpivot_core.format(col_header="ni", periods=staff_unpivot_ni) + """) as ni 
    ON ni.period = sal.period AND ni.staff_line_id = sal.staff_line_id
INNER JOIN 
(""" + staff_unpivot_core.format(col_header="pension", periods=staff_unpivot_pension) + """) as pen 
    ON pen.period = sal.period AND pen.staff_line_id = sal.staff_line_id
INNER JOIN 
(""" + staff_unpivot_core.format(col_header="travel", periods=staff_unpivot_travel) + """) as travel
    ON travel.period = sal.period AND travel.staff_line_id = sal.staff_line_id
INNER JOIN 
(""" + staff_unpivot_core.format(col_header="sp", periods=staff_unpivot_spine) + """) as spine
    ON spine.period = sal.period AND spine.staff_line_id = sal.staff_line_id
"""


def _view():
    return o("v_calc_staff_tabulated", sql)
