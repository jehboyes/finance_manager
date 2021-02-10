"""
View for generating forecasting view core.
"""
from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.database.views import _generate_p_string, get_headers


def _ps(tbl, up_to, desc):
    "Generates Period Split SQL for case statement used in splitting."
    op = "<=" if up_to else ">"
    text_op = "to" if up_to else "from"
    sql = f"SUM(CASE WHEN {tbl}f.period {op} c.split_at_period THEN ISNULL({tbl}f.amount,0) ELSE 0 END) \
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
    periods = _generate_p_string('({p})', ", ")
    periods = f"(SELECT * FROM (VALUES {periods}) AS X(period)) as p"
    sql_1 = f"""
	SELECT s.set_id, acc.summary_code,
			{cases}, 
		   SUM(ISNULL(af.amount, 0)) as prev_actual_total, 
		   SUM(ISNULL(bf.amount, 0)) as mri_total
	FROM conf_forecast c
	CROSS JOIN fs_account acc
	CROSS JOIN {periods}
	INNER JOIN f_set s ON s.acad_year = c.acad_year
						AND s.set_cat_id = c.set_cat_id
	{_join('a', 'comp_acad_year_a', 'comp_set_cat_a')}
	{_join('b', 'acad_year', 'comp_set_cat_b')}
	{_join('main', 'acad_year', 'comp_set_cat_main')}
	GROUP BY s.set_id, acc.summary_code"""
    sql_1_cols = get_headers(sql_1, "x")
    sql_2 = f"""
	SELECT ISNULL(f.forecast_id,-1) as forecast_id, {sql_1_cols}, ISNULL(f.amount, 0) as forecast_amount, 
				ISNULL(f.amount, 0) + x.cur_actual_to_p as forecast_total, 
				(ISNULL(f.amount, 0) + x.cur_actual_to_p - x.mri_total) * e.coefficient * -1 as var_to_mri, 
				f.notes 
	FROM ({sql_1}) as x 
	LEFT OUTER JOIN input_forecast f ON f.set_id = x.set_id AND f.summary_code = x.summary_code 
	INNER JOIN fs_summary_code sc ON x.summarY_code = sc.summary_code
	INNER JOIN fs_account acc ON sc.default_account = acc.account
	INNER JOIN fs_entry_type e ON acc.default_balance = e.balance_type
	"""
    view = o("v_calc_forecast", sql_2)
    return view
