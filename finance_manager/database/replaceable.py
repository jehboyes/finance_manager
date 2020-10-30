"""
Classes required to implement replaceable db object migrations

Creating and updating views or stored procedures can be achieved in alembic migrations
by using the classes here. Note that migrations are manual: they will not be reflected in autogenerate.

https://alembic.sqlalchemy.org/en/latest/cookbook.html#replaceable-objects

Also adds a stamp to show that the object was created externally and shouldn't be directly modified in the database
"""

from alembic.operations import Operations, MigrateOperation
from datetime import datetime
from getpass import getuser
import pkg_resources  # part of setuptools
version = pkg_resources.require("finance_manager")[0].version

stamp = f"""
-- ===================================================
--              FINANCE MANAGER OBJECT
--
-- N.B. Do not alter directly: alterations made 
--      may be overwritten by future migrations.
--
-- Last updated:  {datetime.today()}
-- FM version:    [{version}] 
-- Update run by: {getuser()}
-- ===================================================
"""


class ReplaceableObject(object):
    """
    A database object which can be updated via `DROP` & `CREATE`

    Parameters
    ----------
    name: str
        Name of the object
    sqltext: str
        SQL definition of object
    """

    def __init__(self, name, sqltext):
        self.name = name
        self.sqltext = sqltext


class ReversibleOp(MigrateOperation):
    def __init__(self, target):
        self.target = target

    @classmethod
    def invoke_for_target(cls, operations, target):
        op = cls(target)
        return operations.invoke(op)

    def reverse(self):
        raise NotImplementedError()

    @classmethod
    def _get_object_from_version(cls, operations, ident):
        version, objname = ident.split(".")

        module = operations.get_context().script.get_revision(version).module
        obj = getattr(module, objname)
        return obj

    @classmethod
    def replace(cls, operations, target, replaces=None, replace_with=None):

        if replaces:
            old_obj = cls._get_object_from_version(operations, replaces)
            drop_old = cls(old_obj).reverse()
            create_new = cls(target)
        elif replace_with:
            old_obj = cls._get_object_from_version(operations, replace_with)
            drop_old = cls(target).reverse()
            create_new = cls(old_obj)
        else:
            raise TypeError("replaces or replace_with is required")

        operations.invoke(drop_old)
        operations.invoke(create_new)


@Operations.register_operation("create_view", "invoke_for_target")
@Operations.register_operation("replace_view", "replace")
class CreateViewOp(ReversibleOp):
    def reverse(self):
        return DropViewOp(self.target)


@Operations.register_operation("drop_view", "invoke_for_target")
class DropViewOp(ReversibleOp):
    def reverse(self):
        return CreateViewOp(self.target)


@Operations.register_operation("create_function", "invoke_for_target")
@Operations.register_operation("replace_function", "replace")
class CreatefunctionOp(ReversibleOp):
    def reverse(self):
        return DropfunctionOp(self.target)


@Operations.register_operation("drop_function", "invoke_for_target")
class DropfunctionOp(ReversibleOp):
    def reverse(self):
        return CreatefunctionOp(self.target)


@Operations.implementation_for(CreateViewOp)
def create_view(operations, operation):
    operations.execute("DROP VIEW IF EXISTS %s" % (
        operation.target.name))
    operations.execute("CREATE VIEW %s AS\r %s \r %s" % (
        operation.target.name,
        stamp,
        operation.target.sqltext
    ))


@Operations.implementation_for(DropViewOp)
def drop_view(operations, operation):
    operations.execute("DROP VIEW %s" % operation.target.name)


@Operations.implementation_for(CreatefunctionOp)
def create_function(operations, operation):
    operations.execute("DROP FUNCTION IF EXISTS %s" % operation.target.name)
    operations.execute(
        "CREATE FUNCTION %s \n %s \n %s" % (
            operation.target.name,
            stamp,
            operation.target.sqltext
        )
    )


@Operations.implementation_for(DropfunctionOp)
def drop_function(operations, operation):
    operations.execute("DROP FUNCTION %s" % operation.target.name)
