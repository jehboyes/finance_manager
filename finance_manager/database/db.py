
from finance_manager.database.spec import Base
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

    def __init__(self, engine_string=None, verbose=False, config=None, debug=False):
        if debug:
            #Work in memory
            engine_string = "sqlite:///:memory:"
        elif config is not None:
            engine_string = sa_con_string(dialect=config.read('dialect'),
                                          server=config.read('server'),
                                          db=config.read('database'),
                                          py_driver=config.read('py_driver'),
                                          user=config.read('user'),
                                          password=config.read('password'),
                                          driver=config.read('driver'))
        self._engine = create_engine(engine_string, echo=verbose)
        self._sfactory = sessionmaker(bind=self._engine)

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        self._engine.dispose()
        pass

    def session(self):
        """
        Returns an SQLAlchemy session object
        """
        s = self._sfactory
        return s
