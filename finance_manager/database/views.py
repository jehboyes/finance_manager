from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.functions import periods
p = [f'p{n}' for n in periods()]
p_sum_string = "+".join(p)
p_list_string = ", ".join(p)

account_description = "a.account + ' ' + a.description as account_description"

views = [o("v_input_inc_other", f"""
            SELECT i.inc_id, i.account, a.description as account_name, {account_description}, i.description, i.set_id,
            {p_list_string}, {p_sum_string} as amount
            FROM input_inc_other i
            LEFT OUTER JOIN fs_account a ON i.account = a.account
            """),

         o("v_input_nonp_other", f"""
            SELECT i.nonp_id, i.account, a.description as account_name, {account_description}, i.description, i.set_id,
            {p_list_string}, {p_sum_string} as amount
            FROM input_nonp_other i
            LEFT OUTER JOIN fs_account a ON i.account = a.account
            """),

         o("v_input_pay_claim", f"""
            SELECT i.set_id, i.claim_id, i.account, i.description, {account_description}, i.rate, t.description as claim_type,
	        a.description as account_name,
	        {p_list_string}, {p_sum_string} as hours, ({p_sum_string})*i.rate as amount
            FROM input_pay_claim i
            LEFT OUTER JOIN input_pay_claim_type t ON i.claim_type_id = t.claim_type_id
            LEFT OUTER JOIN fs_account a ON i.account = a.account
            """),
         o("v_fs_account", f"""
            SELECT a.account, a.description, {account_description}, 
            s.description as summary_description, s.section_id
            FROM fs_account a
            INNER JOIN fs_summary_code s ON s.summary_code = a.summary_code 
            WHERE a.hide_from_users = 0
         """)

         ]
