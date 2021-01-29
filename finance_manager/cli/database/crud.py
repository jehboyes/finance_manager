# pylint: disable=no-member
import click
import sys
from tabulate import tabulate
from sqlalchemy import and_
from finance_manager.database import DB
from finance_manager.database.spec import table_map


@click.command()
@click.argument("cmd", type=click.Choice(['create', 'read', 'update', 'delete']))
@click.argument("table", type=str)
@click.option("--where", "-w", multiple=True, help="Filter which records can be affected as `field=value'")
@click.option("--value", "-v", multiple=True, help="Specify values as 'field=value'")
@click.pass_obj
def crud(config, cmd, table, where, value):
    """Command for CRUD operations.

    Perform Create, Read, Delete & Update options (passed as CMD) on TABLE.
    Create and Update require at least 1 VALUE option to be passed;
    Update and Delete require at least 1 WHERE option to be passed.
    WHERE and VALUE options can be passed multiple times.
    """
    c = 'create'
    r = 'read'
    u = 'update'
    d = 'delete'
    with DB(config=config, verbose=True) as db:
        s = db.session()
        # Map the table to the relevant orm object
        table_object = table_map[table]
        # Generate key values pairs from where and values
        wheres = _gen_filters(where, table_object)
        values = _gen_kargs_dict(value)
        if cmd == c:
            record = table_object(**values)
            click.echo("Create: " + _record_to_dict(table_object, record))
            s.add(record)
        elif cmd == r:
            click.echo(r)
            results = s.query(table_object).filter(*wheres).limit(30)
            results_list = []
            for r in results.all():
                results_list.append(
                    [getattr(r, col) for col in table_object.__table__.columns.keys()])
            click.echo(
                tabulate(results_list, headers=table_object.__table__.columns.keys()))
            sys.exit()
        elif cmd == u:
            click.echo(u)
            records = s.query(table_object).filter(*wheres).all()
            for r in records:
                for attr, val in values.items():
                    setattr(r, attr, val)
                click.echo("Updated record: " +
                           _record_to_dict(table_object, record))
        elif cmd == d:
            click.confirm("Confirm delete submission", abort=True)
            q = s.query(table_object).filter(*wheres)
            click.echo("Records to delete:")
            for r in q.all():
                click.echo(_record_to_dict(table_object, r))
            q.delete()
        else:
            click.echo(
                f"Invalid argument: must be one of {c}, {r}, {u} or {d}")
            sys.exit()
        if click.confirm("Commit?"):
            s.commit()
        else:
            s.rollback()


def _gen_kargs_dict(lst):
    """Creates a dictionary, to be unpacked as kargs for ORM work.

    If obj passed, uses the class name to prefix  
    """
    return {a.split("=")[0]: a.split("=")[1] for a in list(lst)}


def _gen_filters(lst, obj):
    return tuple(getattr(obj, f.split("=")[0]) == f.split("=")[1] for f in lst)


def _record_to_dict(tbl, record):
    return {col: getattr(record, col) for col in tbl.__table__.columns.keys()}
