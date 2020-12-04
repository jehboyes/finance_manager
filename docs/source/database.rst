Database Maintenance
====================

Views
-----

Views are defined in the ``finance_manager.database.views`` package. 

Each view is defined in its own module in the views package, which shares a name with the actual view. 
For example, the view 'v_finance' is defined in ``finance_manager/database/views/v_finance.py``. 

View definition is done in this way to allow for dynamic and automated definition of views. This is particularly useful for:

-  Defining views that have a column for each accounting period, which would be laborious 'by hand'
-  Defining pivoted views in such a way that additional values are automatically added as additional columns. 

The views package has a function ``get_views()`` which detects all its modules that define views, and so all that's 
required to document a view is to create the file. The actual detection is automatic. 

To push/replace a view in the database, use the ``fm database syncviews`` CLI command. Note that a view is (intentionally) 
not automatically deleted from the database if its module is deleted. Views must be dropped manually.  

Tables
------

The ``fm.database`` package contains precise definitons of all tables. 

Tables are are defined using the 
`SQLAlchemy Object Relational Mapper <https://docs.sqlalchemy.org/en/14/orm/index.html>`_ so that: 

1. The use of SQL in the project is minimised (keeping the project as Python-based as possible). 
2. The system becomes more easily portable, as the Alembic package can be used to easily migrate the schema to a new database. 

The tables are detailed below:

.. automodule:: finance_manager.database.spec
    :members: