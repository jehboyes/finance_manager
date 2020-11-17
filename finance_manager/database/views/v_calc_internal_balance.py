from finance_manager.database.replaceable import ReplaceableObject as o


def _view():
    inner_sql = """
        SELECT fs.costc, i.costc as contra_costc, fs.acad_year, fs.set_cat_id, 
        SUM(i.amount * -1 * e.coefficient) as total
        FROM input_nonp_internal i
        LEFT OUTER JOIN fs_account a ON i.account = a.account
        LEFT OUTER JOIN fs_entry_type e ON e.balance_type = a.default_balance
        INNER JOIN f_set fs ON fs.set_id = i.set_id
        GROUP BY i.costc, fs.costc, fs.acad_year, fs.set_cat_id
    """
    outer_sql = f"""
    SELECT base.*, contra.total as contra_total, ISNULL(base.total,0)+ISNULL(contra.total,0) as net
    FROM 
    ({inner_sql}) as base
    LEFT OUTER JOIN 
    ({inner_sql}) as contra 
        ON contra.costc = base.contra_costc 
        AND contra.acad_year = base.acad_year 
        AND base.costc = contra.contra_costc 
        AND base.set_cat_id = contra.set_cat_id"""
    return o("v_calc_internal_balance", outer_sql)
