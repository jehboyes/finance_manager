# pylint: disable=no-member
import click
import csv
import sys
import os
from datetime import datetime
from tabulate import tabulate
from sqlalchemy import and_, Table, MetaData, Integer, Column
from finance_manager.database import DB
from finance_manager.database.spec import table_map, meta
from sqlalchemy.ext.automap import automap_base


@click.command()
@click.argument("cmd", type=click.Choice(['create', 'read', 'update', 'delete']))
@click.argument("table", type=str)
@click.option("--where", "-w", multiple=True, help="Filter which records can be affected as 'field=value'")
@click.option("--value", "-v", multiple=True, help="Specify values as 'field=value'")
@click.option("--export", "-e", is_flag=True, help="Export output from 'read' command.")
@click.pass_obj
def crud(config, cmd, table, where, value, export):
    """
    Command for CRUD operations.

    Perform Create, Read, Delete & Update options (passed as CMD) on TABLE.
    Create and Update require at least 1 VALUE option to be passed;
    Update and Delete require at least 1 WHERE option to be passed.
    WHERE and VALUE options can be passed multiple times.
    Use double quotes around strings that contain spaces,
    and enter datetimes as #YY-MM-DD# or #YY-MM-DD-HH-MM#.
    """
    c = 'create'
    r = 'read'
    u = 'update'
    d = 'delete'
    with DB(config=config) as db:
        s = db.session()
        try:
            # Map the table to the relevant orm object
            table_object = table_map[table]

        except:
            if not cmd == r:
                # Fail if trying to do anything but read
                raise ValueError(
                    "Only tables can be passed to create, update or delete.")
            else:
                auto_meta = MetaData()
                table_object = Table(
                    table, auto_meta, Column(
                        'dummy_id', Integer, primary_key=True), autoload=True, autoload_with=db._engine)
                auto_base = automap_base(metadata=auto_meta)
                auto_base.prepare()
                table_object = getattr(auto_base.classes, table)
        # Generate key values pairs from where and values
        wheres = _gen_filters(where, table_object)
        values = _gen_kargs_dict(value)
        # CREATE
        if cmd == c:
            record = table_object(**values)
            click.echo(_record_to_dict(table_object, record))
            s.add(record)
        # READ
        elif cmd == r:
            click.echo(r)
            valid_cols = [
                c for c in table_object.__table__.columns.keys() if c != 'dummy_id']
            results = s.query(*[getattr(table_object, c)
                                for c in valid_cols]).filter(*wheres)
            results_list = []
            if not export:
                results = results.limit(30)
            for r in results.all():
                results_list.append(
                    [getattr(r, col) for col in valid_cols])
            if export:
                filename = f"{table}_export_{'_'.join(where)}_{datetime.today().strftime('%Y%m%d%H%m%S')}.csv"
                filepath = os.path.expanduser('~\\documents\\') + filename
                with open(filepath, "w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(
                        file, quoting=csv.QUOTE_NONE, escapechar='|')
                    writer.writerow(valid_cols)
                    # Unlikely to actually show bar due to speed of write.
                    for row in results_list:
                        row = [a.replace(',', '-') if isinstance(a, str) else a
                               for a in row]
                        writer.writerow(row)
                click.echo(f"{len(results_list)} rows written to {filepath}")
            else:
                click.echo(
                    tabulate(results_list, headers=table_object.__table__.columns.keys()))
            sys.exit()
        # UPDATE
        elif cmd == u:
            click.echo(u)
            records = s.query(table_object).filter(*wheres).all()
            for r in records:
                for attr, val in values.items():
                    if val == 'NULL':
                        setattr(r, attr, None)
                    else:
                        setattr(r, attr, val)
                click.echo(_record_to_dict(table_object, r))
        # DELETE
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
    d = {}
    for i in lst:
        s = i.split("=")
        if s[1] == "NULL":
            s[1] = None
        elif s[1][0] == "#" and s[1][-1] == "#":
            s[1] = s[1].replace("#", "")
            v = [int(x) for x in s[1].split("-")]
            s[1] = datetime(*v)
        elif s[1].lower() == 'false':
            s[1] = False
        elif s[1].lower() == 'true':
            s[1] = True
        d.update({s[0]: s[1]})
    return d


def _gen_filters(lst, obj):
    return tuple(getattr(obj, f.split("=")[0]) == f.split("=")[1] for f in lst)


def _record_to_dict(tbl, record):
    return {col: getattr(record, col) for col in tbl.__table__.columns.keys()}
