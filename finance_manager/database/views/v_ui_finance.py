# pylint: disable=no-member

from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.config import Config
from finance_manager.database import DB
from finance_manager.database.spec import finance_instance, f_set
from finance_manager.database.views import _get_set_cols


def _view(session):
    """
    Return UI view.

    Complex view, which requires a dynamic pivot.
    """
    pvt_list = _get_set_cols(session)
    sql = f"""
    SELECT costc, summary_code, summary, section, supersection, summary_order, sec_order, super_order, level, {pvt_list}
    FROM (SELECT costc, summary_code, summary, section, supersection, summary_order, sec_order, super_order, level,  
            CAST(f_Set.acad_year as CHAR(4)) + ' ' + f_set.set_cat_id as finance_summary, amount as amount
        FROM [v_mri_finance_grouped_subtotal] f INNER JOIN f_set ON f_set.set_id = f.set_id) p
    PIVOT
    (SUM(amount) FOR finance_summary in ({pvt_list})) as pvt
        """
    view = o("v_ui_finance", sql)
    return view
