from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views import p_sum_string
from finance_manager.database.views.v_ui_finance import _get_set_cols
from finance_manager.config import Config


def _view():
    c = Config()
    c.set_section("planning")
    inner_sql = f"""
        SELECT f.directorate_id, f.finance_summary, f.account, a.description, SUM(amount) as t
        FROM v_mri_finance f
        INNER JOIN f_set s ON s.set_id = f.set_id 
        INNER JOIN fs_account a ON a.account = f.account
        WHERE amount <> 0 AND a.summary_code = 301
        GROUP BY f.directorate_id, f.finance_summary, f.account, a.description
    """
    set_cols = _get_set_cols(
        c, auto_format=False)  # want a list returned, not string
    sum_cols = ", ".join([f"ISNULL([{col}], 0) as [{col}]" for col in set_cols])
    set_cols = ", ".join([f"[{col}]" for col in set_cols])
    outer_sql = f"""
    SELECT directorate_id, account as Account, description as Descripton, {sum_cols} 
    FROM ({inner_sql}) pvt
    PIVOT
    (SUM(t) for finance_summary in ({set_cols})) as p
    """
    view = o("v_cons_breakdown", outer_sql)
    return view
