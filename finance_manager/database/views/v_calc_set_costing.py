"""
Calculates the proportions by which loss-making areas
are costed back to income-generators.

Uses the set_costing table for how to cost, 
and defaults to HE courses proportionally according to income. 
"""
from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.functions import periods


def _f(field):
    """SQL for casting as float"""
    return(f"CAST({field} AS FLOAT)")


def _view():
    # Get costing defaults
    default_base = """
    SELECT v.finance_summary{set_option}, SUM(CASE WHEN v.account < 2000 THEN v.amount ELSE 0 END * v.coefficient) as balance 
    FROM v_mri_finance v
    INNER JOIN f_set s ON s.set_id = v.set_id
    WHERE s.curriculum_hours > 0 AND s.surpress=0 --Filter for active curriculum areas only
    AND NOT v.account IN (9801, 9802, 4370, 4360)  --Do not include existing recharges, so that this view is useful to view breakdown 
    GROUP BY v.finance_summary{set_option}
    HAVING SUM(v.amount*v.coefficient) < 0 --Filter for net income generators only
    """
    default_numerator = default_base.format(set_option=", s.set_id, s.costc")
    default_denominator = default_base.format(set_option="")
    default_costing = f"""
    SELECT n.costc, n.finance_summary, {_f("n.balance")}/{_f("d.balance")} as proportion
    FROM ({default_numerator}) as n 
    INNER JOIN ({default_denominator}) as d ON n.finance_summary = d.finance_summary
    """
    # Normalised set costing
    set_costing = f"""
    SELECT n.set_id, n.costc, {_f("n.base_proportion")}/{_f("d.total_proportion")} as proportion
    FROM f_set_costing as n 
    INNER JOIN (SELECT set_id, SUM(base_proportion) as total_proportion 
                FROM f_set_costing GROUP BY set_id) as d ON n.set_id = d.set_id 
    """
    # Cost out loss generators
    loss_makers = """
    Select set_id, finance_summary, SUM(amount*coefficient) as balance FROM v_mri_finance
    WHERE NOT account in (9801,9802) 
    GROUP BY set_id, finance_summary
    HAVING SUM(amount*coefficient) > 0
    """
    base_costings = f"""
    --Get the overriden sets
    SELECT a.set_id, a.balance, b.costc as contra_costc, b.proportion, {_f("a.balance")} * b.proportion as costed_Proportion
    FROM ({loss_makers}) as a 
    INNER JOIN ({set_costing}) as b ON a.set_id = b.set_id
    UNION ALL 
    --Apply the default to all and remove those that do have overrides 
    SELECT a.set_id, a.balance, b.costc as contra_costc, b.proportion, {_f("a.balance")} * b.proportion as costed_Proportion
    FROM ({loss_makers}) as a
    INNER JOIN ({default_costing}) as b ON a.finance_summary = b.finance_summary
    LEFT OUTER JOIN f_set_costing c ON c.set_id = a.set_id    
    WHERE c.set_id IS NULL
    """
    # Get the set ids of the set being costed to, and create contras
    final_core = f"""
    SELECT CASE mod.switch WHEN -1 THEN s1.set_id
                           ELSE s2.set_id END AS set_id, 
           c.costed_proportion as amount, 
           CASE mod.switch WHEN -1 THEN 9801
                           ELSE 9802 END as account, 
            mod.switch as coefficient, 
            CASE mod.switch WHEN -1 THEN s2.costc 
                            ELSE s1.costc END as contra_costc
    FROM ({base_costings}) as c
    INNER JOIN f_set s1 ON c.set_id = s1.set_id
    INNER JOIN f_set s2 ON s2.costc = c.contra_costc AND 
                           s2.acad_year = s1.acad_year AND
                           s2.set_cat_id = s1.set_cat_id 
    CROSS JOIN (SELECT * FROM (VALUES (1), (-1)) as x(switch)) as mod"""

    final_core = final_core.replace("\t", "\t\t")
    final = f"""
    SELECT v.account, v.amount, v.coefficient, 1 as period, 
            s.costc, s.acad_year, s.set_cat_id, c.directorate_id, a.summary_code, 
            '' as description, NULL as instance_id, v.set_id, a.hide_from_users, 
            a.description as account_description, 
            CAST(s.acad_year as CHAR(4)) + ' ' + s.set_cat_id as finance_summary, 
            v.contra_costc, v.coefficient*v.amount*-1 as intuitive_amount      
    FROM ({final_core}) v
    INNER JOIN f_set s ON v.set_id = s.set_id 
    INNER JOIN fs_cost_centre c ON s.costc = c.costc
    INNER JOIN fs_account a ON a.account = v.account
    """
    v = o("v_calc_set_costing", final)
    return v


if __name__ == "__main__":
    print(_view().sqltext)
