import click
import progressbar
import csv
import os
import sys

from finance_manager.database.spec import table_map, f_set, f_set_cat
from finance_manager.database.db import DB
from finance_manager.config import Config

pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@pass_config
def fm(config):
    """
    Finance Manager application.

    This application was designed to be a single point of reference for administration tasks.
    """
    pass


@fm.command()
@click.option("--overwrite", is_flag=True, help="Clear table first")
@click.argument("table_name")
@click.argument("filepath")
@pass_config
def load(config, overwrite, table_name, filepath):
    """
    Load records into a table 
    """
    if table_name not in table_map.keys():
        raise ValueError("Invalid table")

    if not os.path.isfile(filepath):
        raise ValueError("Invalid filepath")
    table = table_map[table_name]
    with DB(config=config) as db:
        session = db.session()
        try:
            if overwrite:
                click.echo("Deleting existing records")
                session.query(table).delete()
            with open(filepath, newline='') as f:
                rdr = csv.reader(f)
                # Load into memory
                rows = [row for row in rdr]
                click.echo(f"{len(rows)} rows found in file")
                first_row = True
                for i in progressbar.progressbar(range(len(rows))):
                    if first_row:
                        labels = [val for val in rows[i]]
                        first_row = False
                    else:
                        values = {x[0]: x[1] for x in zip(labels, rows[i])}
                        record = table(**values)
                        session.add(record)
            click.echo("Committing")
            session.commit()
            click.echo("Success")
        except Exception as inst:
            session.rollback()
            click.echo(inst)


@fm.group()
@pass_config
def sets(config):
    """
    Manage finance sets

    A set is a unique combination of cost centre, academic year, and type.
    Set type is detailed seperately in set code.
    """
    pass


@sets.group()
@pass_config
def codes(config):
    pass


@codes.command()
@click.option('--overwrite', is_flag=True, help="Overwrite existing value if exists")
@click.argument('code')
@click.argument('description')
@pass_config
def add(config, code, description, overwrite):
    """
    Add a new set category
    """
    new_code = f_set_cat(set_cat_id=code, description=description)
    with DB(config=config) as db:
        session = db.session()
        try:
            session.add(new_code)
            session.commit()
        except:
            if overwrite:
                session.query(f_set)


@fm.group()
@pass_config
def settings(config):
    """
    Edit local configuration settings
    """


@settings.command()
@pass_config
def lst(config):
    """
    List available settings
    """
    section = config.section
    print("Environment: ")
    print(section)
    print("-"*len(section))
    print(config.read_section())


@settings.command()
@click.option("--env", type=str)
@click.argument("pairs", nargs=-1)
@pass_config
def set(config, pairs, env):
    """
    Takes key:value pairs and adds/updates as neccesary
    """
    # change env if passed
    if env is not None:
        config.set_env(env)
    # And the actual values, if passed
    try:
        pairs = {p[0]: p[1] for p in [pair.split(":") for pair in pairs]}
        config.write(pairs)
    except:
        print("Set command failed. Check key:value argument(s) valid. ")


@fm.group()
@pass_config
def test(config):
    """
    Test connections and functionality
    """
    pass


@test.command()
@pass_config
def db(config):
    """
    Test database
    """
    db = DB(config=config)
    print(db.engine_string)


"""
Planned layout:

fm
    sets
        list ~list of sets, optional filters
        create ~ create new sets, accept all

    test ~ arguments: appviews, etc

"""
