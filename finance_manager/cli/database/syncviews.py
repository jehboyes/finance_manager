# pylint: disable=no-member
import click
from finance_manager.database.views import get_views
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
@click.option("--test", is_flag=True, help="Attempt to run views after creation.")
@click.option("--restrict", type=str, help="Restrict to a named view.")
@click.pass_obj
def syncviews(config, test, restrict):
    """
    Update database views.

    Pushes view definitions from this application's database views.  
    """
    with DB(config=config) as db:
        views = get_views()
        ordering = [n for n in range(len(views))]
        # Establish dependency
        swap_occurred = True
        i = 0
        lim = 100000
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
        pb_label = "Updating views"
        if test:
            pb_label += " and testing in database"
        with click.progressbar(views, label=pb_label) as bar:
            for v in bar:
                if restrict is None or v.name == restrict:
                    sql = f"\nDROP VIEW IF EXISTS {v.name}"
                    db.con.execute(sql)
                    sql = f"CREATE VIEW {v.name} AS {stamp}\n{v.sqltext}"
                    db.con.execute(sql)
                    if test:
                        _ = db.con.execute(f"SELECT * FROM {v.name}").fetchall()
