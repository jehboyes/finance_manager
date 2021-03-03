# pylint: disable=no-member

from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.config import Config
from finance_manager.database import DB
from finance_manager.database.spec import finance_instance, f_set


def _view():
    """
    List of transactions. 

    Only used for (proper) forecasting sets, i.e. those that have a 
    set_cat_id where ``is_forecast`` is true. 
    """
    sql = """
    SELECT t.set_id, t.transaction_id, 
        sc.description as summary_desc, sc.position as summary_order, 
        ty.description as type, s.description as status, 
        t.dt, ISNULL(t.supplier_name, 'n/a') as supplier, t.description as description, SUM(t.amount) as amount
    FROM f_transaction t 
    INNER JOIN f_transaction_type ty ON ty.type_id = t.type_id
    INNER JOIN f_transaction_status s ON s.status_id = t.status_id
    INNER JOIN fs_account a ON a.account = t.account 
    INNER JOIN fs_summary_code sc ON sc.summary_code = a.summary_code
    GROUP BY t.set_id, t.transaction_id, sc.description, sc.position, ty.description, s.description, t.dt, t.supplier_name, t.description 
    """
    return o("v_transaction", sql)
