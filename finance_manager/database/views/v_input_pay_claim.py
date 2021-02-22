from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views import account_description, _generate_p_string

period_list = _generate_p_string("p{p}", ", ")
amount = "+".join([_generate_p_string("p{p}*adjusted_rate", "+"),
                   _generate_p_string("ni_p{p}", "+"),
                   _generate_p_string("pension_p{p}", "+")]) + " as amount"

sql = f"""
SELECT set_id, claim_id, description, CASE claim_type_id WHEN 'CAS' THEN 2102 ELSE account END as account, 
    CASE claim_type_id WHEN 'CAS' THEN '2102 Casual Claims' ELSE account_description END as account_description, 
    rate, claim_type, claim_type_id, 
{period_list}, {amount}
FROM v_calc_claim
"""


def _view():
    return o("v_input_pay_claim", sql)
