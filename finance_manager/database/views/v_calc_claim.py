from finance_manager.functions import periods
from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views import account_description, _generate_p_string, _sql_bound


# Claim rate of pay
rate_calculation = "ROUND((isnull(i.rate, 0)*variable_rate+rate_uplift)*base_multiplier*holiday_multiplier, 2)"

# Need own period list (instead of from views) as need alias prefix
i_periods = _generate_p_string("i.p{p} as p{p}", ",")
i_periods_summed = _generate_p_string("i.p{p}", "+")
# estimating national_insurance by period - take off an estimate of hourly threshold, multiply by rate
ni_periods = ",\n".join(
    ["("+_sql_bound("MAX", f"{rate_calculation}-ni.p{n}/37", "0")+f")*i.p{n}*ni.rate*t.apply_ni as ni_p{n}" for n in periods()])


def _spine(sp):
    """Return spine point value (SQL)

    Parameters
    ----------
    sp : int
        Spine point
    """
    return f"(SELECT value/365*7/37 FROM staff_spine WHERE spine = {sp})"


# estimating pension by period - none for casual, then a sliding scale fomr 0% to 100% of possible contribution,
# up to grade 7.
pension_periods = ",\n".join(
    ["("+_sql_bound("MIN", "1", f"({rate_calculation}-{_spine(4)})/({_spine(33)}-{_spine(4)})") +
        f")*i.p{n}*{rate_calculation}*t.apply_pension*pen.p{n} as pension_p{n}" for n in periods()])

sql = f"""
SELECT i.set_id, i.claim_id, i.account, i.description,
{account_description}, i.rate, {rate_calculation} as adjusted_rate,
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
