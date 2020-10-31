import click

from finance_manager.database import DB
from sqlalchemy import text
from tabulate import tabulate


@click.command()
@click.option("--database", type=str, help="Which DB to query.")
@click.option("--rows", type=int, help="Maximum number of rows.", default=5)
@click.argument("dbobject")
@click.pass_obj
def preview(config, dbobject, rows, database):
    """
    Show a preview of a table or view. 
    """
    # Pick database
    if database is None:
        config.set_section("planning")
    else:
        config.set_section(database)
    with DB(config=config) as db:
        sql = text(f"SELECT TOP {rows} * FROM {dbobject}")
        headers = db.con.execute(sql).keys()
        values = db.con.execute(sql).fetchall()
        click.echo(tabulate(values, headers=headers))
