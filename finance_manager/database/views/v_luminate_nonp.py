from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views import p_sum_string, _generate_p_string
from finance_manager.database.views.v_ui_finance import _get_set_cols


def _view(session):
    inner_sql = f"""
        SELECT f.directorate_id, f.finance_summary, f.account, a.description, SUM(amount) as t
        FROM v_mri_finance f
        INNER JOIN f_set s ON s.set_id = f.set_id 
        INNER JOIN fs_account a ON a.account = f.account
        WHERE amount <> 0 AND a.summary_code = 301 AND s.surpress = 0
        GROUP BY f.directorate_id, f.finance_summary, f.account, a.description
    """
    set_cols = _get_set_cols(
        session, auto_format=False)  # want a list returned, not string
    sum_cols = ", ".join([f"ISNULL([{col}], 0) as [{col}]" for col in set_cols])
    set_cols = ", ".join([f"[{col}]" for col in set_cols])
    p_list = _generate_p_string("a.p{p}", ", ")
    sum_p_list = _generate_p_string("SUM(p{p}) as p{p}", ", ")
    outer_sql = f"""
    SELECT a.set_cat_id, a.acad_year, b.*, {p_list} 
	FROM 
    (SELECT c.directorate_id, s.set_cat_id, s.acad_year, account_name, account, {sum_p_list}
	FROM v_input_nonp_other v
	INNER JOIN f_set s ON s.set_id = v.set_id 
	INNER JOIN fs_cost_centre c ON c.costc = s.costc 
	GROUP BY c.directorate_id, s.set_cat_id, s.acad_year, account_name, account) as a
	INNER JOIN 
	(SELECT directorate_id, p.account as Account, p.description as Description, {sum_cols} 
    FROM ({inner_sql}) pvt
    PIVOT
    (SUM(t) for finance_summary in ({set_cols})) as p
    ) as b ON a.directorate_id = b.directorate_id AND a.account = b.Account
    
    """
    view = o("v_luminate_nonp", outer_sql)
    return view
