from finance_manager.database.replaceable import ReplaceableObject as o

levels = [['summary_code', '1', 'summary_code', 'a'],
          ['sub_section', '2', 'sub_section_id', 's1'],
          ['section', '3', 'section_id', 's2'],
          ['super_section', '5', 'super_section_id', 's3']]

sec_fields = ",\n".join(
    [f"s{a[1]}.{a[2]}, s{a[1]}.description as {a[0]}_description" for a in levels])
sec_source = "\n".join(
    [f"INNER JOIN fs_{a[0]} s{a[1]} ON s{a[1]}.{a[2]} = {a[3]}.{a[2]}" for a in levels])
# group = ", ".join([f"s{a[1]}.{a[2]}, s{a[1]}.description" for a in levels])

acc_source = "LEFT OUTER JOIN fs_account acc_{x} ON acc_{x}.account = {x}.account \n" \
             "LEFT OUTER JOIN fs_entry_type e_{x} ON e_{x}.balance_type = acc_{x}.default_balance"

fields = "i.instance_id, i.datestamp, i.created_by, i.set_id, prev.prev_instance, f.costc, f.set_cat_id, f.acad_year, cc.directorate_id"

finance_table = "SELECT account, period, instance_id, SUM(Amount) as amount FROM f_finance GROUP BY account, period, instance_id"


def _view():
    inner_sql = f"""
    --Converts each finance instance into the difference to its predecessor, 
    --meaning the results can be stacked (rather than taking 'census points'). 
    SELECT COALESCE(a.instance_id, b.join_instance) as instance_id, 
    COALESCE(a.account, b.account) as account, 
    COALESCE(a.period, b.period) as period, 
    COALESCE(a.amount,0.00) - COALESCE(b.amount, 0.00)  as amount
    FROM 
    ({finance_table}) a 
    FULL OUTER JOIN 
    (SELECT prev.instance_id as join_instance, x.* FROM 
    (SELECT MAX(b.instance_id) as prev_instance, a.instance_id
    FROM f_finance_instance a
    LEFT OUTER JOIN f_finance_instance b ON a.set_id = b.set_id
    WHERE b.instance_id < a.instance_id GROUP BY a.instance_id) prev 
    INNER JOIN ({finance_table}) x ON x.instance_id = prev.prev_instance
    )
    b ON b.join_instance = a.instance_id
                            AND b.account = a.account
                            AND b.period = a.period
    WHERE ISNULL(a.amount,0.00) - ISNULL(b.amount, 0.00) <> 0.00
    """

    sql = f"""
    SELECT fi.datestamp, fi.instance_id, i.account as account, i.period, i.amount * e.coefficient * -1.0 as amount, 
        fs.costc, fs.set_cat_id, fs.acad_year, cc.directorate_id, d.description as directorate_description, cc.costc + ' ' + cc.description as costc_desc, 
        fs.surpress, 
        {sec_fields}
    FROM ({inner_sql}) as i 
    INNER JOIN f_finance_instance fi ON fi.instance_id = i.instance_id
    INNER JOIN f_set fs ON fs.set_id = fi.set_id
    INNER JOIN fs_cost_centre cc ON cc.costc = fs.costc
    INNER JOIN fs_directorate d ON d.directorate_id = cc.directorate_id
    INNER JOIN fs_account a ON i.account = a.account
    INNER JOIN fs_entry_type e ON e.balance_type = a.default_balance
    {sec_source}
    WHERE i.amount <> 0.00
    """

    return o("v_maint_fhistory", sql)
