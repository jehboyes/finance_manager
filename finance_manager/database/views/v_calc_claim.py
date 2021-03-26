"""
This view takes the inputs from the input_pay_claim table, and calculates the 
resultant costs. 

Base rate calculation
~~~~~~~~~~~~~~~~~~~~~

In SQL, the calculation is:
``ROUND((ISNULL(i.rate, 0)*variable_rate+t.rate_uplift)*base_multiplier*holiday_multiplier, 2)``

The first variable ``ISNULL(i.rate,0)`` takes the input rate, and replaces missing values with 0. 
The rest of the variables all belong to the table :py:class:`finance_manager.database.spec.claim_type`. 

The calculation translates to 'Overwrite the hourly rate if applicable (e.g. for minimum wage claims), increase for
general uplift if applicable (e.g. teaching prep time), and increase to account for 
an appropriate amount of holiday pay if applicable'.  

National Insurance
~~~~~~~~~~~~~~~~~~

The amount of NI payable is estimated by comparing the above hourly rate to the NI 
`weekly secondary threshold <https://www.gov.uk/guidance/rates-and-thresholds-for-employers-2020-to-2021#class-1-national-insurance-thresholds>`_ 
divided by 37. The portion of the hourly rate above this threshold (if the portion is greater than 0)
is multiplied the NI contribution rate for band A. 

There is an apply_ni flag in the :py:class:`finance_manager.database.spec.claim_type` table that can subvert this process, 
which is True when the amount entered is intended as a lump sum, rather than something else. 

Pension
~~~~~~~

The :py:class:`finance_manager.database.spec.claim_type` table has a flag that controls whether or not to add employers pension 
contibutions to the claim. If true, the most expensive contribution rate is applied to the hourly rate.   

"""

from finance_manager.functions import periods
from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views import account_description, _generate_p_string, _sql_bound


# Claim rate of pay
rate_calculation = "ROUND((ISNULL(i.rate, 0)*variable_rate+t.rate_uplift)*base_multiplier*holiday_multiplier, 2)"

# Need own period list (instead of from views) as need alias prefix
i_periods = _generate_p_string("i.p{p} as p{p}", ",")
i_periods_summed = _generate_p_string("i.p{p}", "+")
# estimating national_insurance by period - take off an estimate of hourly threshold, multiply by rate
ni_periods = ",\n".join(
    ["("+_sql_bound("MAX", f"{rate_calculation}-ni.p{n}/37", "0")+f")*i.p{n}*ni.rate*t.apply_ni as ni_p{n}" for n in periods()])

# Heavily simplified pension calculation - applied to anything not casual
pension_periods = _generate_p_string(
    "i.p{p}*" + rate_calculation + "*t.apply_pension*pen.p{p} as pension_p{p}", ",\n")

sql = f"""
SELECT i.set_id, i.claim_id, CASE i.claim_type_id WHEN 'CAS' THEN 2102 ELSE i.account END as account, 
i.description,
CASE i.claim_type_id WHEN 'CAS' THEN '2102 Casual Claims' ELSE a.account + ' ' + a.description END as account_description, 
i.rate, {rate_calculation} as adjusted_rate,
t.description as claim_type, t.claim_type_id,
a.description as account_name,
{i_periods},
{ni_periods},
{pension_periods},
({i_periods_summed})*{rate_calculation} as amount
FROM input_pay_claim i
LEFT OUTER JOIN input_pay_claim_type t ON i.claim_type_id = t.claim_type_id
LEFT OUTER JOIN fs_account a ON i.account = a.account
INNER JOIN f_set s ON s.set_id = i.set_id
INNER JOIN staff_ni ni ON ni.acad_year = s.acad_year
INNER JOIN staff_pension_contrib pen ON pen.pension_id = 'WP' AND pen.acad_year = s.acad_year
"""


def _view():
    view = o("v_calc_claim", sql)
    return view


if __name__ == "__main__":
    print(sql)
