# pylint: disable=no-member
import click
import os
import progressbar
import csv as csv_
from finance_manager.database import DB
from finance_manager.database.spec import table_map


@click.command()
@click.option("--overwrite", is_flag=True, help="Clear table first")
@click.argument("table_name")
@click.argument("filepath")
@click.pass_obj
def loadcsv(config, overwrite, table_name, filepath):
    """
    Load records into a table. 

    Appends all the records from ``FILEPATH`` to ``TABLE_NAME``. The column headings in the file 
    are required to match those in the table (though not all need to be present).  
    """
    if table_name not in table_map.keys():
        raise ValueError("Invalid table")

    if not os.path.isfile(filepath):
        raise ValueError("Invalid filepath")
    table = table_map[table_name]
    with DB(config=config) as db:
        session = db.session()
        try:
            if overwrite:
                click.echo("Deleting existing records")
                session.query(table).delete()
            with open(filepath, newline='') as f:
                rdr = csv_.reader(f)
                # Load into memory, to get count of rows
                rows = [row for row in rdr]
                click.echo(f"{len(rows)} rows found in file")
                first_row = True
                records = []
                for i in progressbar.progressbar(range(len(rows))):
                    if first_row:
                        labels = [val for val in rows[i]]
                        first_row = False
                    else:
                        values = {x[0]: x[1]
                                  for x in zip(labels, rows[i]) if len(x[1]) > 0}
                        records.append(values)
            click.echo("Committing...")
            session.bulk_insert_mappings(table, records)
            session.commit()
            click.echo("Success")
        except Exception as inst:
            session.rollback()
            click.echo(inst)
