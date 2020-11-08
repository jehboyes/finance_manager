from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views import account_description, p_list_string, p_sum_string


def _view():
    view = o("v_input_nonp_other", f"""
    SELECT i.nonp_id, i.account, a.description as account_name, {account_description}, i.description, i.set_id,
    {p_list_string}, {p_sum_string} as amount
    FROM input_nonp_other i
    LEFT OUTER JOIN fs_account a ON i.account = a.account
            """)
    return view
