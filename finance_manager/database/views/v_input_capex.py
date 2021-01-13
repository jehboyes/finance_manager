from finance_manager.database.replaceable import ReplaceableObject as o


def _view():
    view = o("v_input_capex", f"""
    SELECT i.*, 
        i.amount_furniture + amount_equipment + i.amount_it + i.amount_building as total_amount,
        i.title + ': Total £' + CAST(i.amount_furniture + amount_equipment + i.amount_it + i.amount_building as varchar(10)) as summary, 
        p.ordering 
    FROM input_capex i
    LEFT OUTER JOIN input_capex_reason r ON r.reason_id = i.reason_id
    LEFT OUTER JOIN input_capex_priority p ON p.priority_id = i.priority_id 
            """)
    return view
