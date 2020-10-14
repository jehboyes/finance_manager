class periods:
    """
    Iterator for periods

    Exists for brevity/clarity in actual code
    """

    def __init__(self):
        pass

    def __iter__(self):
        self.a = 1
        return self

    def __next__(self):
        if self.a <= 12:
            x = self.a
            self.a += 1
            return x
        else:
            raise StopIteration


def sa_con_string(dialect, server, db,  py_driver=None, user=None, password='', driver=None):
    """
    Formats connection variables into SQL Alchemy string



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
    """
    # Configure security
    if user is not None:
        login = user + ':' + password
        trust = ''
    else:
        login = ''
        trust = '?trusted_connection=yes'

    # Configure dialect
    if py_driver is not None:
        dialect = '+'.join([dialect, py_driver])

    # configure additional dialect
    if driver is not None:
        driver = '&driver='+driver.replace(" ", "+")

    con = f"{dialect}://{login}@{server}/{db}{trust}{driver}"

    return con
