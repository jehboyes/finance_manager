from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views.v_mri_finance_grouped_subtotal import sql

source = """FROM v_mri_finance f 
LEFT OUTER JOIN fs_summary_code sc ON sc.summary_code = f.summary_code
LEFT OUTER JOIN fs_sub_section sub ON sub.sub_section_id = sc.sub_section_id
LEFT OUTER JOIN fs_section s ON s.section_id = sub.section_id 
LEFT OUTER JOIN fs_super_section super ON super.super_section_id = s.super_section_id
WHERE sc.summary_code in (302, 503, 901, 902) --the internal transaction lines
"""

mod_sql = sql.replace("WHERE", "AND")


def _view():
    return o("v_mri_finance_grouped_subtotal_internal", mod_sql.format(source=source))
