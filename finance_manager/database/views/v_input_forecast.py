"""
View for forecasting.
"""
from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views import _generate_p_string


def _ps(tbl, up_to, desc):
    "Generates Period Split SQL for case statement used in splitting."
    op = "<=" if up_to else ">"
    text_op = "to" if up_to else "from"
    sql = f"SUM(CASE WHEN {tbl}.period {op} c.split_at_period THEN {tbl}.amount ELSE 0 END) \
			as {desc}_{text_op}_p"
    return sql


def _join(alias, year_field, cat_field):
    sql = f"""
	--Join on {year_field} and {cat_field}
	LEFT JOIN f_set {alias} ON {alias}.acad_year = c.{year_field}
						AND {alias}.set_cat_id = c.{cat_field}
						AND {alias}.costc = s.costc
	LEFT JOIN v_mri_finance {alias}f ON {alias}f.set_id = {alias}.set_id
								AND {alias}f.account = acc.account
								AND {alias}f.period = p.period
	"""
    return sql


def _view():
    case_list = [['a', True, 'prev_actual'],
                 ['a', False, 'prev_actual'],
                 ['b', True, 'mri'],
                 ['b', False, 'mri'],
                 ['main', True, 'cur_actual']]
    cases = ",\n".join([_ps(a[0], a[1], a[2]) for a in case_list])
    periods = "(SELECT * FROM \
		(VALUES {_generate_p_string('({p})', ", ")}) AS X(period)) as p"
    inner_sql = f"""
	SELECT s.set_id, acc.summary_code,
			{cases}
	FROM conf_forecast c
	CROSS JOIN fs_account acc
	CROSS JOIN {periods}
	INNER JOIN f_set s ON s.acad_year = c.acad_year
						AND s.set_cat_id = c.set_cat_id
	{_join('a', 'prev_acad_year', 'comp_set_cat_a')}
	{_join('b', 'acad_year', 'comp_set_cat_b')}
	{_join('main', 'acad_year', 'comp_set_cat_main')}
	GROUP BY s.set_id, acc.summary_code"""
    sql = f"""
	SELECT x.*, f.amount as forecast_amount
	FROM ({inner_sql}) as x
	LEFT OUTER JOIN input_forecast f ON f.set_id = x.set_id AND f.summary_code = x.summary_code"""
    view = o("v_input_forecast", sql)
    return view
