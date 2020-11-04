from finance_manager.database.views import account_description, p_list_string, p_sum_string
from finance_manager.database.replaceable import ReplaceableObject as o

view = o("v_input_pay_claim", f"""
SELECT i.set_id, i.claim_id, i.account, i.description, {account_description}, i.rate,
t.description as claim_type, t.claim_type_id,
a.description as account_name,
{p_list_string}, {p_sum_string} as hours,
({p_sum_string})*(ISNULL(i.rate,0)*t.variable_rate+t.rate_uplift)*t.base_multiplier*t.holiday_multiplier as amount
FROM input_pay_claim i
LEFT OUTER JOIN input_pay_claim_type t ON i.claim_type_id = t.claim_type_id
LEFT OUTER JOIN fs_account a ON i.account = a.account
            """),
