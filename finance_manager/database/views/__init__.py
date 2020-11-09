"""
Contains defintions for the more complex views, i.e. those which explicitly reference multiple period columns

Handy strings are at the top, then actual views are imported from the namesake files in this directory. 
Slowly moving all views to their own files, which each contain one view: files are read by importing them using importlib. 

TODO Split this file into grouped versions
"""
import importlib
from os import listdir, path

from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.functions import periods

# List of named periods
p = [f'p{n}' for n in periods()]
# p1 + ... + p12
p_sum_string = "+".join(p)
# p1, ... , p12
p_list_string = ", ".join(p)
# Shorthand, as needs to be standardised
account_description = "a.account + ' ' + a.description as account_description"

# work out a line's monthly FTE
staff_month_sal = ", \n".join(
    [f"dbo.udfGetMonthProp(f_set.acad_year, {n}, s.start_date, s.end_date)*vFTE.FTE*(ss.value+ISNULL(s.allowances,0))/12 as p{n}"
     for n in periods()])
staff_month_sal_total = ", \n".join(
    [f"SUM(m.p{n}) as p{n}" for n in periods()])
staff_month_ni = ", \n".join(
    [f"ISNULL(dbo.udfNI(mt.p{n}, ni.p{n}, ni.rate)*m.p{n}/NULLIF(ISNULL(NULLIF(mt.p{n},0),m.p{n}),0),0) as ni_p{n}" for n in periods()])
staff_month_pension = ", \n".join(
    [f"m.p{n}*ISNULL(pension.p{n},0) as pension_p{n}" for n in periods()])
staff_travel_months = 9
staff_travel_allowance = ", \n ".join(
    [f"s.travel_scheme/{staff_travel_months} as travel_p{n}" for n in range(3, 3+staff_travel_months)])


def _sql_bound(max_or_min, *fields):
    """
    Produces sql to return the maximum of two fields. 

    Parameters
    ----------
    max_or_min : str
        One of MAX or MIN, depending on behaviour desired. 
    fields : str
        Field names of the inputs to the max/min function. 
    """
    cmd = max_or_min.upper()
    if cmd != "MAX" and cmd != "MIN":
        raise ValueError("Invalid command: must be MAX or MIN")
    field_str = ",".join([f"({field})" for field in fields])
    sql = f"SELECT {max_or_min}(n) FROM (VALUES {field_str}) as value(n)"
    return sql


def _generate_p_string(str_format, join_with=None, restrict=None):
    """Generates a list of periods in the given format.

    Use {n} where the period numebr is required in the format string. 

    Parameters
    ----------
    format : str
        String to format with the period number.
    join_with : str
        If passed, joins the list with the given path
    restrict : int 
        If n passed, restricts the output to the first n periods 
    """
    if restrict is None:
        restrict = 12
    lst = [str_format.format(p=n) for n in periods(restrict)]
    if join_with is not None:
        lst = join_with.join(lst)
    return lst


def get_views():
    """
    Return a list of views as replaceable objects. 

    Defined as a function rather than a list to avoid code running on compilation. Each file in this folder should define a funciton `_view` which returns a replaceable object, which is 
    a simple class defined in replaceable. 
    """
    # Detect files defined in directory
    p = path.dirname(__file__)
    files = listdir(p)
    modules = [importlib.import_module(
        ".."+f[:-3], "finance_manager.database.views.") for f in files if f[:2] == "v_"]
    view_list = [module._view() for module in modules]
    return view_list
