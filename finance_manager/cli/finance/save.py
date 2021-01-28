# pylint: disable=no-member
import click
from datetime import datetime
from sqlalchemy import and_, text
from getpass import getuser
from finance_manager.database import DB
from finance_manager.database.spec import f_set, finance, finance_instance
from finance_manager.database.views.v_calc_finances import _view
from collections import defaultdict


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

        # Get sets to be updated
        sets = session.query(f_set).filter(and_(f_set.acad_year == acad_year,
                                                f_set.set_cat_id == setcat))
        if restrict != None:  # add costc filter if passed
            click.echo(f"Restricting to {restrict}")
            sets = sets.filter(f_set.costc == restrict)
        sets = sets.all()

        # Calculate the actual finances
        click.echo("Calculating finances...", nl=False)
        calc_finances = session.execute(
            f"SELECT account, period, amount, set_id FROM {_view().name}")
        click.echo("Complete.")

        # COnvert the results to a dictionary by set_id for easier processing
        dict_finances = defaultdict(list)
        for r in calc_finances:
            dict_finances[r[3]].append(r)

        # For each set (wrapped for progress bar)
        with click.progressbar(sets, label="Working through sets", show_eta=False, item_show_func=_progress_label, fill_char="£") as bar:
            for s in bar:
                # Make it a finance set
                i = finance_instance(created_by=getuser(),
                                     set_id=s.set_id, datestamp=datetime.now())
                session.add(i)
                session.flush()
                # create a list of finance objects for buk inserting, way quicker than one by one
                finances = []
                for row in dict_finances[s.set_id]:
                    finances.append(finance(instance_id=i.instance_id,
                                            account=row[0], period=row[1], amount=row[2]))
                session.bulk_save_objects(finances)
                session.commit()


def _progress_label(s):
    if s is not None:
        return f"Processing {s.costc}"
