# pylint: disable=no-member
import click
from datetime import datetime
from sqlalchemy import and_, text
from getpass import getuser
from finance_manager.database import DB
from finance_manager.database.spec import f_set, finance, finance_instance
from finance_manager.database.views.v_calc_finances import _view


@click.command()
@click.argument("acad_year", type=int)
@click.argument("setcat", type=str)
@click.option("--restrict", type=str, help="Only save 1 cost centre (passed to this option).")
@click.pass_obj
def save(config, acad_year, setcat, restrict=None):
    """
    Save all matching sets.

    Create a finance instance for each set with the given ``ACAD_YEAR`` and ``SETCAT``.  
    """
    with DB(config=config) as db:
        session = db.session()
        sets = session.query(f_set).filter(and_(f_set.acad_year == acad_year,
                                                f_set.set_cat_id == setcat))
        if restrict != None:  # add costc filter if passed
            click.echo(f"Restricting to {restrict}")
            sets = sets.filter(f_set.costc == restrict)
        sets = sets.all()
        with click.progressbar(sets, label="Working through sets") as bar:
            for s in bar:
                # Make it a finance set
                i = finance_instance(created_by=getuser(),
                                     set_id=s.set_id, datestamp=datetime.now())
                session.add(i)
                session.flush()
                sql = f"""INSERT INTO {finance.__tablename__} (instance_id, account, period, amount) 
                        SELECT {i.instance_id}, account, period, amount FROM {_view().name} WHERE set_id = {s.set_id}"""
                session.execute(sql)
                session.commit()
