import functools
import click


class periods():
    """
    Iterator for periods

    Exists for brevity/clarity in actual code
    """

    def __init__(self, end=12):
        self.end = end
        pass

    def __iter__(self):
        self.a = 1
        return self

    def __next__(self):
        if self.a <= self.end:
            x = self.a
            self.a += 1
            return x
        else:
            raise StopIteration


def period_to_month(period, acad_year):
    """
    Financial month and year to calendar month and year.    

    Converts a period and academic year into the actual month number and calendar year.

    Parameters
    ----------
    period : int
        Accounting period
    acad_year : int
        Academic year (calendar year commencing)
    """
    # Because August is P1
    period += 7
    # Increment calendar year if new period is in next year (i.e. >12)
    acad_year += (period-1)//12
    # Bring period back to legitimate month number, and correct for 0
    period = period % 12
    if period == 0:
        period = 12
    return period, acad_year


def sa_con_string(dialect, server, db,  py_driver=None, user=None, password='', driver=None):
    """
    Formats connection variables into SQL Alchemy string

    ...

    Parameters
    ----------
    dialect : str
        SQLAlchemy-recognised name for the DBMS, such as `mssql` or `sqlite`
    server : str
        Server/host name 
    db : str
        Database name 
    py_driver : str
        Name of additional driver required for dialect connection (e.g. pyodbc)
    user : str
        Username, if used. If ommitted, connection uses windows credentials (via trusted connection)
    password : str
        Password for given username. Can be blank
    driver : str
        Specific driver to use when connecting  

    Returns
    -------
    str
        SQL Alchemy engine connection string
    """
    # Configure security
    user = '' if user is None else user
    if len(user) > 0:
        login = user + ':' + password
        trust = ''
    else:
        login = ''
        trust = '?trusted_connection=yes'

    # Configure dialect
    if py_driver is not None:
        dialect = '+'.join([dialect, py_driver])

    # configure additional dialect
    if driver is not None and len(driver) > 0:
        driver = '&driver='+driver.replace(" ", "+")

    con = f"{dialect}://{login}@{server}/{db}{trust}{driver}"

    return con


def slow_line(func, before_text, after_text, show=True):
    """
    Prints text before and after a line has executed
    """
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        if show and before_text is not None:
            click.echo(before_text, nl=False)
        value = func(*args, **kwargs)
        if show and after_text is not None:
            click.echo(after_text)
        elif show:  # Carriage return
            click.echo()
        return value
    return wrapper_decorator
