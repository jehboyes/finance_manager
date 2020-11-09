# pylint: disable=no-member
import click
from finance_manager.database.views import get_views
from finance_manager.database import DB
from datetime import datetime
from getpass import getuser
import pkg_resources  # part of setuptools
version = pkg_resources.require("finance_manager")[0].version

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
    view_list = get_views()
    with DB(config=config) as db:
        with click.progressbar(view_list, label="Updating views") as bar:
            for v in bar:
                if restrict is None or v.name == restrict:
                    sql = f"\nDROP VIEW IF EXISTS {v.name}"
                    db.con.execute(sql)
                    sql = f"CREATE VIEW {v.name} AS {stamp}\n{v.sqltext}"
                    db.con.execute(sql)
        if test:
            with click.progressbar(view_list, label="Testing views") as bar:
                for v in bar:
                    if restrict is None or v.name == restrict:
                        _ = db.con.execute("SELECT * FROM " + v.name).fetchall()
