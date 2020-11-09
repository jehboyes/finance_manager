Database Specification
======================

The database directory conatians precise definitons of all of the tables, views and stored procedures required of the database the application is built on. 

This exists so that: 
1. The use of SQL in the CLI is significantly reduced, using instead the SQLAlchemy ORM. 
2. The system becomes more easily portable, as the Alembic package can be used to migrate the specified data structures to a new database. 

.. automodule:: finance_manager.database.spec
    :members:
    :undoc-members:
    :show-inheritance:
