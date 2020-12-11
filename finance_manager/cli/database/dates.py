# pylint: disable=no-member
import click

from sqlalchemy import and_
from finance_manager.database import DB
from finance_manager.database.spec import dt


@click.command()
@click.option("-d", "--delete", is_flag=True, help="Delete set cat's dates.")
@click.argument("acad_year", type=int)
@click.argument("set_cat", type=str)
@click.argument("date", type=click.DateTime)
@click.argument("date_cat", type=str)
@click.argument("description", type=str)
@click.pass_obj
def preview(config, delete, acad_year, set_cat=None, date=None, date_cat=None, description=None):
    """
    Add or remove dates. 

    Defaults to adding a date with the parameters specified.
    """
    # determine route
    with DB(config=config) as db:
        session = db.session()
        if delete:
            q = session.query(dt).filter(and_(dt.acad_year == acad_year,
                                              dt.set_cat_id == set_cat))
            l = len(q.fetch())
            if l > 0:
                if click.confirm(f"Delete {l} dates?"):
                    q.delete()
                    session.commit()
            else:
                click.echo(f"No dates found")
        else:
            d = dt(acad_year=acad_year, set_cat_id=set_cat, dt=date,
                   dt_cat_id=date_cat, description=description)
            session.add(d)
            session.commit()
