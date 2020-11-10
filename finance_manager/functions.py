"""
These are a collection of generic functions, classes and iterators intended for use in various parts of the App, 
and will probably be of use to future development. 
"""
import functools
import click


class periods():
    """
    Iterator for financial periods.

    Exists for brevity/clarity in actual code. Outputs the numbers 1 to 12, 
    unless restricted by passing the ``end`` parameter on construction. 
    """

    def __init__(self, end=12):
        """
        Parameters
        ----------
        end : int, optional
            The final month to output, useful for dynamic in-year processing, but by default 12. 
        """
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

    Returns
    -------
    tuple
        Month, Calendar year

    Examples
    --------
    Period 1 (August) in the 2020 financial year:

    >>> period_to_month(1,2020)
    (8, 2020)

    Period 6 (January) in the 1984 financial year: 

    >>> period_to_month(6, 1984)
    (1, 1985)
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
    Formats connection variables into SQL Alchemy string.

    Intended for brevity elsewhere in the App. For more detail, 
    see the `SQLAlchemy Engine Configuration <https://docs.sqlalchemy.org/en/13/core/engines.html>`_ page. 

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
        Password for given username. Can be blank. 
    driver : str
        Specific driver to use when connecting.

    Returns
    -------
    str
        SQL Alchemy engine connection string.
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


def level_to_session(level):
    """
    Converts study level to a year of study. 

    Intended for use with the level descriptions that come out of the 
    HE In Year Cohort web report, but applicable to other instances. 

    Parameters
    ----------
    level : str
        The text version of a level. Should begin with the word 'level'.

    Returns
    -------
    int
        The year of study that the level (typically) corresponds to.
    """

    session = "X"
    if level[:5].upper() == "LEVEL":
        session = int(level[-1]) - 3
    else:
        session = 1
    return session


def name_to_aos(name):
    """
    Converts a verbose course name to its aos_code

    Essentially a fuzzy matching function, intended for use with reverse engineering web reports

    Parameters
    ----------
    name : str
        The course description. Can include year. 

    Returns
    -------
    str
        The 6-character aos_code. 
    int
        Session, i.e. year of study. If no numeric characters were 
        in the ``name``, this will default to -1.

    Examples
    --------
    >>> name_to_aos('Jazz Year 1')
    ('HBAMJA', 1)

    When no numeric year information appears

    >>> name_to_aos('Jazz Year Two')
    ('HBAMJA', -1)
    """
    aos_abbr = [["Business", "BU", ""],
                ["Classical", "CM", "C"],
                ["Film", "FM"],
                ["Folk", "FO", "F"],
                ["Jazz", "JA", "J"],
                ["Production", "PR", "M"],
                ["Popular", "PM", "P"],
                ["Songwriting", "SW"],
                ["Acting", "ACT"],
                ["Actor Musician", "AMU"],
                ["Musical Theatre", "MTH"]]
    aos_code = ""
    if name[:2] == "BA":
        aos_code = "HBA"
        if "with" in name:
            # i.e. is combined
            aos_code += "C"
            withpos = name.index("with")
            for p in aos_abbr:
                if p[0] in name[:withpos]:
                    aos_code += p[2]
            for p in aos_abbr:
                if p[0] in name[withpos:]:
                    aos_code += p[2]
        else:  # Music and Acting/MT
            if " Music (" in name:
                aos_code += "M"
            for p in aos_abbr:
                if p[0] in name:
                    aos_code += p[1]
                    break
    elif "Foundation Degree" in name or "FD" in name:
        aos_code = "HFD"
        if "Electronic" in name or "EMP" in name:
            aos_code += "EMP"
        else:
            aos_code += "MPM"
    elif "Creative" in name or "MMus" in name:
        aos_code = "HMMCRM"
    if len(aos_code) != 6:
        raise ValueError(
            f"Unable to recognise {name}. Got as far as '{aos_code}''.")
    # And then the numeric bit
    num = -1
    for char in name:
        if char.isdigit():
            num = int(char)
            break

    return aos_code, num
