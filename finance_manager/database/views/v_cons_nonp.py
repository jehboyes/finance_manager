from finance_manager.database.replaceable import ReplaceableObject as o

sql = f"""
SELECT s.costc, s.acad_year, s.set_cat_id, cc.directorate_id,
v.account AS Account, v.account_description AS [Account Name],
v.description as [Description], v.amount AS Amount
FROM v_input_nonp_other v
INNER JOIN f_set s ON v.set_id = s.set_id
INNER JOIN fs_cost_centre cc ON cc.costc = s.costc
WHERE amount <> 0
"""


def _view():
    return o("v_cons_nonp", sql)
