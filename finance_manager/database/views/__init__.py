# pylint: disable=no-member
"""
Contains functions for the more complex views, such as those which explicitly reference multiple period columns.

Handy strings are at the top, then actual views are imported from the namesake files in this directory.
View files are read by importing them using importlib.

Views under construction/not ready for deployment have their files prefixed with an underscore.
"""
import importlib
import inspect
from os import listdir, path

from finance_manager.database.replaceable import ReplaceableObject as o
from finance_manager.functions import periods
from finance_manager.database import DB
from finance_manager.database.spec import f_set, finance_instance

# List of named periods
p = [f'p{n}' for n in periods()]
# p1 + ... + p12
p_sum_string = "+".join(p)
# p1, ... , p12
p_list_string = ", ".join(p)
# Shorthand, as needs to be standardised
account_description = "a.account + ' ' + a.description as account_description"
# Shorthand for finance summary (set summary) description
finance_summary = "cast(s.acad_year as varchar) + ' ' + s.set_cat_id as finance_summary"


def _sql_bound(max_or_min, *fields):
    """
    Produces sql to return the maximum of two fields.

    Parameters
    ----------
    max_or_min : str
        One of MAX or MIN, depending on behaviour desired.
    fields : str
        Field names of the inputs to the max/min function.

    Returns
    -------
    str
        String like 'SELECT [MAX or MIN](n) FROM (VALUES) as VALUE(n)'
    """
    cmd = max_or_min.upper()
    if cmd != "MAX" and cmd != "MIN":
        raise ValueError("Invalid command: must be MAX or MIN")
    field_str = ",".join([f"({field})" for field in fields])
    sql = f"SELECT {max_or_min}(n) FROM (VALUES {field_str}) as value(n)"
    return sql


def _generate_p_string(str_format, join_with=None, restrict=None):
    """Generates a list of periods in the given format.

    Use {p} where the period number is required in the format string.

    Parameters
    ----------
    format : str
        String to format with the period number.
    join_with : str
        If passed, joins the list with the given path
    restrict : int
        If n passed, restricts the output to the first n periods

    Returns
    -------
    list
        List of numbers from 1 to 12 (or less if restrict was passed)
    """
    if restrict is None:
        restrict = 12
    lst = [str_format.format(p=n) for n in periods(restrict)]
    if join_with is not None:
        lst = join_with.join(lst)
    return lst


def _get_set_cols(session, auto_format=True):
    """
    Return finance_summary strings.

    Only requires database connection. Returns each
    combination of year and set_code_id alraedy in use. For example,
    if 2020 BP1 exists, then [2020 BP1] will be one of the values returned.

    Parameters
    ----------
    session : Object
        SQL Alchemy session object.
    auto_format : boolean
        True returns a string with commas and square braces (for SQL). False returns list.

    Returns
    -------
    str
        SQL compatible list, or list if auto_format set to false.
    """
    col_list = []
    for year, cat in session.query(f_set.acad_year, f_set.set_cat_id).join(finance_instance).distinct():
        name = ' '.join([str(year), cat])
        col_list.append(name)
    pvt_list = ", ".join(f"[{n}]" for n in col_list)
    if auto_format:
        return pvt_list
    else:
        return col_list


def get_views(session):
    """
    Return a list of views as replaceable objects.

    Defined as a function rather than a list to avoid code running on compilation. Each file in this folder should define a funciton `_view` which returns a replaceable object, which is
    a simple class defined in replaceable.

    Parameters
    ----------
    session : Object
        SQL Alchemy session object, because some views header definitions depend on data.
    """
    # Detect files defined in directory
    p = path.dirname(__file__)
    files = listdir(p)
    modules = [importlib.import_module(
        ".."+f[:-3], "finance_manager.database.views.") for f in files if f[:2] == "v_"]
    view_list = []
    for module in modules:
        # Test for whether the view requires a session object for header construction
        if "session" in inspect.getfullargspec(module._view)[0]:
            view_list.append(module._view(session))
        else:
            view_list.append(module._view())
    return view_list


def get_headers(sql, prefix=None):
    """Returns a list of headers in an sql select string"""
    cols = []
    open_parenth = False
    clean_sql = ""
    # Remove anything in parentheses, liable to contain commas
    for i, char in enumerate(sql):
        if char == "(":
            open_parenth = True
        elif char == ")":
            open_parenth = False
        if not open_parenth:
            clean_sql += sql[i].replace("\t", " ")
    for col in clean_sql.split("FROM")[0].replace("SELECT", "").split(","):
        if " as " in col.lower():
            c = col.split(" as ")[-1]
        elif "." in col.lower():
            c = col.split(".")[-1]
        else:
            c = col
        cols.append(c.strip())
    if prefix != None:
        cols = ", ".join([".".join([prefix, col]) for col in cols])
    return cols
