from finance_manager.database.replaceable import ReplaceableObject as o


def _view():
    sql = f"""
    SELECT i.internal_id, i.description, i.account, i.costc, i.set_id, i.amount, 
        i.amount * -1 * e.coefficient as output_amount, 
        CASE WHEN sc.internal = 1 THEN ISNULL(b.net,0) ELSE 0 END as net, 
        a.account + ' ' + a.description as account_description
    FROM input_nonp_internal i
    INNER JOIN f_set fs ON fs.set_id = i.set_id
    LEFT OUTER JOIN fs_account a ON i.account = a.account
    INNER JOIN fs_summary_code sc ON a.summary_code = sc.summary_code 
    LEFT OUTER JOIN fs_entry_type e ON e.balance_type = a.default_balance
    LEFT OUTER JOIN v_calc_internal_balance b 
        ON b.costc=fs.costc 
        AND b.contra_costc = i.costc 
        AND b.set_cat_id = fs.set_cat_id 
        AND b.acad_year = fs.acad_year
        AND b.accf = left(a.account,1)    """
    return o("v_input_nonp_internal", sql)
