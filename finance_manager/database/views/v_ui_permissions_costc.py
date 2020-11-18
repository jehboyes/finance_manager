"""
Exists seperately to other just for the UI's benefit (powerapps groupby is messy). 
"""
from finance_manager.database.replaceable import ReplaceableObject as o


def _view():
    sql = """
    SELECT DISTINCT c.costc, c.description as costc_name, c.costc+' '+c.description as long_name, 
        lower(core.login_365) as login_365
    FROM 
        (
            SELECT costc, owner as login_365 FROM fs_cost_centre
            UNION ALL 
            SELECT costc, login_365 FROM a_permission
            UNION ALL 
            SELECT c.costc, d.director 
            FROM fs_directorate d INNER JOIN fs_cost_centre c ON c.directorate_id = d.directorate_id
        ) as core
    INNER JOIN fs_cost_centre c ON core.costc = c.costc 
    WHERE c.supercede_by IS NULL"""
    return o("v_ui_permissions_costc", sql)
