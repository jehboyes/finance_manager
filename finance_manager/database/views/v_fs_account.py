from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views import account_description, p_list_string, p_sum_string


def _view():
    view = o("v_fs_account", f"""
    SELECT a.account, a.description, {account_description},
    s.description as summary_description, s.section_id
    FROM fs_account a
    INNER JOIN fs_summary_code s ON s.summary_code = a.summary_code
    WHERE a.hide_from_users = 0
         """)
    return view
