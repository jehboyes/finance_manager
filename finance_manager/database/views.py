from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.functions import periods
p = [f'p{n}' for n in periods()]
p_sum_string = "+".join(p)

views = [o("v_input_inc_other", f"""
            SELECT i.account, a.description as account_name,i.description, i.set_id, 
            SUM({p_sum_string}) as amount
            FROM input_inc_other i
            INNER JOIN fs_account a ON i.account = a.account
            GROUP BY i.inc_id, i.account, a.description, i.description, i.set_id"""),

         o("v_input_nonp_other", f"""
            SELECT i.account, a.description as account_name, i.description, i.set_id, 
            SUM({p_sum_string}) as amount
            FROM input_nonp_other i
            INNER JOIN fs_account a ON i.account = a.account
            GROUP BY i.nonp_id, i.account, a.description, i.description, i.set_id"""),

         o("v_input_pay_claim", f"""
            SELECT i.set_id, i.claim_id, i.account, i.description, i.rate, t.description as claim_type, 
	        a.description as account_name,
	        SUM({p_sum_string}) as hours, SUM(({p_sum_string})*i.rate) as amount
            FROM input_pay_claim i 
            INNER JOIN input_pay_claim_type t ON i.claim_type_id = t.claim_type_id
            INNER JOIN fs_account a ON i.account = a.account
            GROUP BY i.set_id, i.claim_id, i.account, i.description, i.rate, t.description, 
                a.description""")

         ]
