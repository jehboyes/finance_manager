from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.functions import periods


def _view():
    # for a period table
    values_clause = ", ".join([f"({n})" for n in periods()])
    view = o("v_input_pay_fracclaim", f"""
    SELECT fs.set_id, ISNULL(fc.hours, 0) as hours, p.period
    FROM f_set fs
    CROSS JOIN
    (SELECT * FROM
        (VALUES {values_clause}) AS X(period)) as p
    LEFT OUTER JOIN input_pay_fracclaim fc ON fc.set_id = fs.set_id AND fc.period = p.period
    """)
    return view
