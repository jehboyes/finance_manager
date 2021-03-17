# pylint: disable=no-member
import click
from datetime import datetime
from sqlalchemy import and_, text, Table
from sqlalchemy.sql import select
from getpass import getuser
from finance_manager.database import DB
from finance_manager.database.spec import f_set, finance, finance_instance, Base
from finance_manager.database.views.v_calc_finances import _view
from collections import defaultdict
from finance_manager.cli.cm.curriculum import curriculum
from finance_manager.database.views.v_calc_set_costing import _view as costing_view_ro


@click.command()
@click.argument("acad_year", type=int)
@click.argument("setcat", type=str)
@click.option("--skip_curriculum", "-c", is_flag=True, help="Skip the curriculum hours update.")
@click.pass_context
@click.pass_obj
def save(config, ctx, acad_year, setcat, skip_curriculum=False):
    """
    Save all matching sets.

    Create a finance instance for each set with the given ``ACAD_YEAR`` and ``SETCAT``.  
    """
    # Update curriculum
    if not skip_curriculum:
        ctx.invoke(curriculum, setcat=setcat, acad_year=acad_year)
    config.set_section("planning")
    with DB(config=config) as db:
        session = db.session()
        # Get sets to be updated
        sets = session.query(f_set).filter(and_(f_set.acad_year == acad_year,
                                                f_set.set_cat_id == setcat))

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
        set_instance_dict = {}
        with click.progressbar(sets, label="Working through sets", show_eta=False, item_show_func=_progress_label, fill_char="£") as bar:
            for s in bar:
                # Make it a finance set
                i = finance_instance(created_by=getuser(),
                                     set_id=s.set_id, datestamp=datetime.now())
                session.add(i)
                session.flush()
                set_instance_dict[s.set_id] = i.instance_id
                # create a list of finance objects for buk inserting, way quicker than one by one
                finances = []
                for row in dict_finances[s.set_id]:
                    finances.append(finance(instance_id=i.instance_id,
                                            account=row[0], period=row[1], amount=row[2]))
                session.bulk_save_objects(finances)
        session.flush()
        session.commit()
        # Work out the recharges based on the values just input, which will then be added to the instances
        costing_view = Table(costing_view_ro().name,
                             Base.metadata,
                             autoload_with=db._engine)
        select_costings = select([costing_view.c.account,
                                  costing_view.c.period,
                                  costing_view.c.amount,
                                  costing_view.c.set_id]) \
            .where(and_(costing_view.c.acad_year == acad_year,
                        costing_view.c.set_cat_id == setcat))
        costings = db.con.execute(select_costings).fetchall()
        # Aggregate to add to an instance
        agg_recharges = defaultdict(float)
        for costing in costings:
            agg_recharges[(costing.account, costing.set_id,
                           costing.period,)] += costing.amount
        finances = []
        for key, amount in agg_recharges.items():
            if amount != 0:
                account, set_id, period = key
                if set_id in set_instance_dict.keys():
                    finances.append(finance(instance_id=set_instance_dict[set_id],
                                            account=account,
                                            period=period,
                                            amount=amount))
                else:
                    print(f"Set {set_id} missing")
        session.bulk_save_objects(finances)
        session.commit()


def _progress_label(s):
    if s is not None:
        return f"Processing {s.costc}"
