from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views import account_description, p_list_string, p_sum_string


def _view():
    view = o("v_fs_section_hierarchy", f"""
    -- Exists just as a reference, to check the categorisation of accounts to super-sections. Built 'right to left'
    SELECT e.super_section_id, e.description as Super, 
			d.section_id, d.description as Section, 
			c.sub_section_id, c.description as SubSection, 
			b.summary_code, b.description as Summary, 
			a.account, a.description as AccountName
    FROM fs_account a
    LEFT OUTER JOIN fs_summary_code b ON b.summary_code = a.summary_code
    LEFT OUTER JOIN fs_sub_section c ON c.sub_section_id = b.sub_section_id
    LEFT OUTER JOIN fs_section d ON d.section_id = c.section_id
    LEFT OUTER JOIN fs_super_section e ON e.super_section_id = d.super_section_id
         """)
    return view
