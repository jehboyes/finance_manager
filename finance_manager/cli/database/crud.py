# pylint: disable=no-member
import click
import sys
import tabulate
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
        # Normalise the command
        cmd = cmd.lcase()
        # Map the table to the relevant orm object
        table_object = table_map[table]
        # Generate key values pairs from where and values
        wheres = _gen_key_values(where)
        values = _gen_key_values(value)
        if cmd == c:
            click.echo(c)
            record = table_object(**values)
            s.add(record)
        elif cmd == r:
            click.echo(r)
            results = s.query(table).filter(and_(**wheres))
            click.echo(
                tabulate(results.all(), headers=results.column_descriptions()))
            sys.exit()
        elif cmd == u:
            click.echo(u)
            records = s.query(table).filter(and_(**wheres)).all()
            for r in records:
                for attr, val in values.items():
                    setattr(r, attr, val)
        elif cmd == d:
            click.confirm("Confirm delete submission", abort=True)
            s.query(table).filter(and_(**where)).delete()
        else:
            click.echo(
                f"Invalid argument: must be one of {c}, {r}, {u} or {d}")
            sys.exit()
        if click.confirm("Commit shown statements?"):
            s.commit()
        else:
            s.rollback()


def _gen_key_values(lst):
    """Creates a dictionary, to be unpacked
    """
    return {a[0]: a[1] for a in lst.split("=")}
