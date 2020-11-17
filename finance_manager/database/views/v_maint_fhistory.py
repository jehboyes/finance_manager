from finance_manager.database.replaceable import ReplaceableObject as o


def _view():
    sql = """
    SELECT CONVERT(VARCHAR,i.datestamp,20) as stamp , s.costc, f.account, (f.amount * e.coefficient) as amount 
    FROM f_finance f 
    INNER JOIN f_finance_instance i ON i.instance_id = f.instance_id 
    INNER JOIN f_set s ON s.set_id = i.set_id
    INNER JOIN fs_account a ON f.account = a.account 
    INNER JOIN fs_entry_type e ON e.balance_type = a.default_balance   
    """

    return o("v_maint_fhistory", sql)
