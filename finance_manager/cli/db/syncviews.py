# pylint: disable=no-member
import click
from finance_manager.database.views import get_views
from finance_manager.database.functions import function_list
from finance_manager.config import Config as conf
from finance_manager.database import DB
from datetime import datetime
from getpass import getuser
import warnings
import finance_manager._version as ver
version = ver.__version__

stamp = f"""
-- ===================================================
--              FINANCE MANAGER OBJECT
--
-- N.B. Do not alter directly: alterations made 
--      may be overwritten by future migrations.
--
-- Last updated:  {datetime.today()}
-- FM version:    [{version}] 
-- Update run by: {getuser()}
-- ===================================================
"""


@click.command()
@click.option("-t", "--test", is_flag=True, help="Attempt to run views after creation.")
@click.option("-r", "--restrict", type=str, help="Restrict to a named view.")
@click.option("-o", "--output", is_flag=True, help="Outputs SQL instead of writing to DB.")
@click.option("-f", "--functions", is_flag=True, help="Also update functions.")
@click.pass_obj
def syncviews(config, test, restrict, output, functions):
    """
    Update database views.

    Pushes view definitions from this application's database views.  
    """
    with DB(config=config) as db:
        session = db.session()
        views = get_views(session)
        ordering = [n for n in range(len(views))]
        # Establish dependency
        swap_occurred = True
        i = 0
        lim = 100000
        if not output:
            click.echo(
                "Determining view dependencies (for ordering CREATE execution)")
        while swap_occurred and i < lim:
            swap_occurred = False
            views = [views[i] for i in ordering]
            ordering = [n for n in range(len(views))]
            for pos_v, v in enumerate(views):
                for pos_vc, vc in enumerate(views):
                    if v.name in vc.sqltext and pos_v > pos_vc:
                        # swap them in the execution order
                        ordering[pos_v] = pos_vc
                        ordering[pos_vc] = pos_v
                        swap_occurred = True
                        i += 1
                        break
                if swap_occurred:
                    break
        if i >= lim:
            warnings.warn(
                f"Ordering **unfinished** after {lim} attempts. Indicative of circular reference in views.", RuntimeWarning)
        views = [views[i] for i in ordering]
        if output:
            pb_label = "View SQL:"
        elif test:
            pb_label = "Updating and testing in DB"
        else:
            pb_label = "Updating views"
        if functions:
            for f in function_list:
                sql = f"\nDROP FUNCTION IF EXISTS {f.name}"
                db.con.execute(sql)
                sql = f"CREATE FUNCTION {f.name} \n {stamp}\n{f.sqltext}"
                db.con.execute(sql)
        with click.progressbar(views, label=pb_label, fill_char="#", item_show_func=_return_name) as bar:
            for v in bar:
                if restrict is None or v.name == restrict:
                    if output:
                        click.echo(v.sqltext)
                    else:
                        sql = f"\nDROP VIEW IF EXISTS {v.name}"
                        db.con.execute(sql)
                        sql = f"CREATE VIEW {v.name} AS {stamp}\n{v.sqltext}"
                        db.con.execute(sql)
                        if test:
                            _ = db.con.execute(
                                f"SELECT * FROM {v.name}").fetchall()


def _return_name(v):
    if v is not None:
        return v.name
