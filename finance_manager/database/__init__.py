
"""
Module for the database class
"""

from finance_manager.functions import sa_con_string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DB():
    """
    Class for handling db connection 

    Intended to be used by being passed a config object

    Parameter
    ---------
    engine_string : str
        SQLAlchemy type string 
    verbose : boolean
        Prints additional information if true 
    config : Config
        Custom config class. If passed, uses the db variables to automatically generate string.  
    """

    def __init__(self, config=None, debug=False):
        self.debug = debug
        if config is not None:
            self.engine_string = sa_con_string(dialect=config.read('dialect'),
                                               server=config.read('server'),
                                               db=config.read('database'),
                                               py_driver=config.read(
                                                   'py_driver'),
                                               user=config.read('username'),
                                               password=config.read(
                                                   'password'),
                                               driver=config.read('driver'))
            self.verbose = config.verbose  # Overwrites previous if config passed
        if self.debug:
            print(self.engine_string)

    def __enter__(self):
        # try:
        self._engine = create_engine(self.engine_string, echo=self.verbose)
        self._sfactory = sessionmaker(bind=self._engine)
        self.con = self._engine.connect()
        # except:
        # raise ConnectionError(
        #     "Unable to connect to database. This may be caused by the connection timing out.")
        return self

    def __exit__(self, type, value, traceback):
        self._engine.dispose()
        pass

    def session(self):
        """
        Returns an SQLAlchemy session object
        """
        s = self._sfactory()
        return s
