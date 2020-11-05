from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views import account_description, generate_p_string

period_list = generate_p_string("p{p}", ", ")
amount = "+".join([generate_p_string("p{p}*adjusted_rate", "+"),
                   generate_p_string("ni_p{p}", "+"),
                   generate_p_string("pension_p{p}", "+")]) + " as amount"

sql = f"""
SELECT set_id, claim_id, description, account, account_description, rate, claim_type, claim_type_id, 
{period_list}, {amount}
FROM v_calc_claim
"""
view = o("v_input_pay_claim", sql)

if __name__ == "__main__":
    print(sql)
