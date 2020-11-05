from finance_manager.database.replaceable import ReplaceableObject as o

view = o("v_cons_staff", f"""SELECT s.costc, s.acad_year, s.set_cat_id, cc.directorate_id, 
Title, ISNULL(name, 'Unnamed') as Name, Grade, 
current_spine as Spine, indicative_fte as FTE, Allowances, 
pay_total as Salary, ni_total as NI, pension_total as Pension, 
pay_total+ ni_total+ pension_total as [Grand Total]
FROM v_input_pay_staff v
INNER JOIN f_set s ON v.set_id = s.set_id
INNER JOIN fs_cost_centre cc ON cc.costc = s.costc
""")
