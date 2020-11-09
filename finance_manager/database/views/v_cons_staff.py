from finance_manager.database.replaceable import ReplaceableObject as o

sql = f"""
SELECT s.acad_year, s.set_cat_id, cc.directorate_id,
Title, ISNULL(name, 'Unnamed') as Name, Grade,
current_spine as Spine, SUM(indicative_fte) as FTE, SUM(Allowances) as Allowances,
SUM(pay_total) as Salary, SUM(ni_total) as NI, SUM(pension_total) as Pension,
SUM(pay_total+ ni_total+ pension_total) as [Grand Total]
FROM v_input_pay_staff v
INNER JOIN f_set s ON v.set_id = s.set_id
INNER JOIN fs_cost_centre cc ON cc.costc = s.costc
GROUP BY s.acad_year, s.set_cat_id, cc.directorate_id,
v.title, v.name, v.grade,
v.current_spine
"""


def _view():
    return o("v_cons_staff", sql)
