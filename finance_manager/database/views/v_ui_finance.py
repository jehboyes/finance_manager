# pylint: disable=no-member

from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.config import Config
from finance_manager.database import DB
from finance_manager.database.spec import finance_instance, f_set


def view():
    """
    Return UI view. 

    Complex view, which requires a dynamic pivot. 
    """
    c = Config()
    c.set_section("planning")
    with DB(config=c) as db:
        session = db.session()
        col_list = []
        for year, cat in session.query(f_set.acad_year, f_set.set_cat_id).join(finance_instance).distinct():
            name = ' '.join([str(year), cat])
            col_list.append(name)
    pvt_list = ", ".join(f"[{n}]" for n in col_list)
    sql = f"""
    SELECT costc, sec, summary_code, sec_order, line_order, format, {pvt_list}
    FROM (SELECT costc, sec, summary_code, sec_order, line_order, finance_summary, format, SUM(amount) as amount 
    FROM [v_mri_finance_grouped_subtotal] GROUP BY costc, sec, summary_code, sec_order, line_order, finance_summary, format) p 
    PIVOT
    (SUM(amount) FOR finance_summary in ({pvt_list})) as pvt    
        """
    view = o("v_ui_finance", sql)
    return view
