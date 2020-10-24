import click
import progressbar
import csv
import os
import sys

from finance_manager.database.spec import table_map, f_set, f_set_cat, pension_emp_cont, ni as ni_table
from finance_manager.database.db import DB
from finance_manager.config import Config
from finance_manager.functions import periods

pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@pass_config
def fm(config):
    """
    Finance Manager application.

    This application was designed to be a single point of reference for administration tasks.
    """
    config.set_section("planning")


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
                # Load into memory, to get count of rows
                rows = [row for row in rdr]
                click.echo(f"{len(rows)} rows found in file")
                first_row = True
                records = []
                for i in progressbar.progressbar(range(len(rows))):
                    if first_row:
                        labels = [val for val in rows[i]]
                        first_row = False
                    else:
                        values = {x[0]: x[1] for x in zip(labels, rows[i])}
                        records.append(values)
            click.echo("Committing...")
            session.bulk_insert_mappings(table, records)
            session.commit()
            click.echo("Success")
        except Exception as inst:
            session.rollback()
            click.echo(inst)


@fm.command()
@click.option("--costc", type=str, help="Limit to a cost centre")
@click.option("--set_id", type=int, help="Limit to an individual set")
@click.option("--cat", type=str, help="Limit to a set category")
@click.option("--year", type=int, help="Limit to an academic year")
@pass_config
def curriculum(config, costc, set_id, cat, year):
    """Update the curriculum hours for all sets

    Use the options to restrict which sets are updated
    """
    config.set_section("cm")  # Get connection variables for curriculum database
    with DB(config=config) as db:  # Connect to curriculum db to get total hours
        hours = db.con.execute(
            "SELECT curriculum_id, costc, hours FROM vCurriculumEnrolsForAppTotal").fetchall()
    hours = {(x[0], x[1]): x[2] for x in hours}
    config.set_section("planning")  # Connection variables for planning database
    with DB(config=config) as db:  # Connect to planning DB
        session = db.session()
        set_list = session.query(f_set)
        if set_id is not None:
            print("check")
            set_list = set_list.filter_by(set_id=set_id)
        else:  # Else at this point used because set_id overwrites other filters
            if costc is not None:
                set_list = set_list.filter_by(costc=costc)
            if cat is not None:
                set_list = set_list.filter_by(set_cat_id=cat)
            if year is not None:
                set_list = set_list.filter_by(acad_year=year)
        sets = set_list.all()
        for s in sets:
            s.curriculum_hours = hours.get((s.curriculum_id, s.costc), 0)
        session.commit()

    db_cm = DB(config=config)


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
@click.option("--overwrite", is_flag=True, help="Overwrite instance if exists")
@click.option("--ni", type=float, help="Alter NI")
@click.argument("year")
@click.argument("preapril")
@click.argument("postapril")
@click.argument("pension", required=False)
def setoncost(config, ni, year, pension, preapril, postapril, overwrite):
    """    
    Set NI or employer's pension contributions in a given year. 

    Creates one record in the relevant table (determined by flagging NI or setting PENSION)
    \f
    \b
    Parameters
    ----------
    config : object
        A finance manager config object
    year : int
        Academic year
    pension_id : str
        2 character pension ID (FK to 'staff_pension' table)
    preapril : float
        Value for months August to March
    postapril : float
        Value for months April to July
    """
    if ni is not None and pension is not None:
        click.echo("Cannot process NI and Pension simultaneously.")
        exit
    if ni is not None:
        table = ni_table
        record = dict(acad_year=year, rate=ni)
    else:
        table = pension_emp_cont
        record = dict(pension_id=pension, acad_year=year)
    for p in periods():
        field = f"p{p}"
        if p < 9:  # Because changes occur at change of tax year in April
            rate = preapril
        else:
            rate = postapril
        record[field] = rate
    with DB(config=config) as db:
        s = db.session()
        existing = s.query(table).filter_by(acad_year=year)
        if pension is not None:
            existing = existing.filter_by(pension_id=pension)
        existing = existing.all()[0]
        if existing is None or overwrite:
            if existing is not None:
                s.delete(existing)
                s.flush()
            s.bulk_insert_mappings(table, [record])
            s.commit()
        else:
            print("Record already exists; use overwrite option to force replacement.")


@settings.command()
@pass_config
def configuration(config):
    """
    List configuration settings.
    """
    section = config.section
    print("Environment: ")
    print(section)
    print("-"*len(section))
    print(config.read_section())


@settings.command()
@click.option("--env", type=str, help="Use this to change the environment")
@click.argument("pairs", nargs=-1)
@pass_config
def set_configuration(config, pairs, env):
    """
    Takes key:value pairs and adds/updates as neccesary.
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
