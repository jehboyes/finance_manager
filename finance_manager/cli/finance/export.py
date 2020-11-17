import click
import os
from datetime import datetime
import csv
from finance_manager.database import DB


@click.command()
@click.argument("acad_year", type=int)
@click.argument("set_cat_id", type=str)
@click.option("--governors", is_flag=True, help="Include governor's budget adjustments.")
@click.pass_obj
def export(config, acad_year, set_cat_id, governors):
    """
    Exports the most recent instances of all cost centres in the given ACAD_YEAR and SET_CAT_ID as
    a csv in the parent directory. 
    """
    with DB(config=config) as db:
        con = db.con
        # specified seperately for writing csv headings later
        fields = ["costc", "account", "period", "amount"]
        sql = f"SELECT {','.join(fields)} FROM v_mri_finance_export WHERE acad_year = {acad_year} AND set_cat_id = '{set_cat_id}'"
        if not governors:
            sql += " AND governors = 0"
        rows = con.execute(sql).fetchall()
    if governors:
        g_flag = "GOV"
    else:
        g_flag = ""
    filename = f"Finance_Export_{acad_year}_{set_cat_id}{g_flag}_{datetime.today().strftime('%Y%m%d%H%m%S')}.csv"
    filepath = os.path.expanduser('~\\documents\\') + filename
    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, quoting=csv.QUOTE_NONE)
        writer.writerow(fields)
        # Unlikely to actually show bar due to speed of write.
        with click.progressbar(rows) as bar:
            for row in bar:
                writer.writerow(row)
    click.echo(f"Written {len(rows)} rows to {filepath}.")
