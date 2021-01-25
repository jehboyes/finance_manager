from finance_manager.database.replaceable import ReplaceableObject as o


def _view():
    view = o("v_ui_finance_breakdown", f"""
    SELECT set_id, summary_code, account, account_description, sum(amount) as amount FROM v_mri_finance
    GROUP BY set_id, summary_code, account, account_description
    """)
    return view
