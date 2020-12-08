# pylint: disable=no-member

import click

from finance_manager.database import DB
from finance_manager.database.spec import ni as ni_table, pension_emp_cont
from finance_manager.functions import periods


@click.command()
@click.option("--overwrite", is_flag=True, help="Overwrite instance if exists")
@click.option("--ni", type=float, help="Alter NI")
@click.argument("year")
@click.argument("preapril")
@click.argument("postapril")
@click.argument("pension", required=False)
@click.pass_obj
def oncost(config, ni, year, pension, preapril, postapril, overwrite):
    """    
    Set NI or employer's pension contributions in a given year. 

    Creates one record in the relevant table (determined by flagging ``NI`` or setting ``PENSION``).
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
        if len(existing.all()) == 0 or overwrite:
            if overwrite and len(existing.all()) == 0:
                s.delete(existing.all()[0])
                s.flush()
            s.bulk_insert_mappings(table, [record])
            s.commit()
        else:
            print("Record already exists; use overwrite option to force replacement.")
