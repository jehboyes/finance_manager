import csv
import click
from sqlalchemy import text
from finance_manager.functions import level_to_session, name_to_aos
from finance_manager.database import DB


@click.command()
@click.argument("filepath", type=str)
@click.argument("usage", type=str)
@click.option("--detect", is_flag=True, help="Detect aos code from verbose data in aos_code.")
@click.pass_obj
def input(config, filepath, usage, detect):
    """
    Input Student Numbers.

    Use a csv (saved at ``FILEPATH``) to update the student numbers with ``USAGE_ID``
    in the curriculum model database. Assumes there is 1 column for each of
    acad_year, aos_code, fee_status_id, session, student_count.

    TODO Add validation checks for input, and try/excepts.
    """
    # Dict of headers required and if string
    headers = {}
    body = []
    years = {}
    with open(filepath, newline="") as file:
        rows = csv.reader(file)
        for i, row in enumerate(rows):
            if i == 0:
                for j, col in enumerate(row):
                    headers.update({col: j})
            else:
                years.update({row[headers['acad_year']]: 0})
                body.append(row[:])
    # instance for each year
    config.set_section("cm")
    with DB(config=config) as db:
        conn = db.con
        trans = conn.begin()
        with click.progressbar(years, label="Writing instances") as bar:
            for acad_year in bar:
                sql = f"""INSERT INTO student_number_instance (acad_year, usage_id, lcom_username, costc)
                        OUTPUT INSERTED.instance_id VALUES({acad_year}, '{usage}', 'CL Interface', 'MA1600')"""
                instance_id = conn.execute(text(sql)).fetchone()[0]
                for row in body:
                    if row[headers['acad_year']] == acad_year:
                        if detect:
                            row[headers['aos_code']] = name_to_aos(
                                row[headers['aos_code']])[0]
                        sql = f"""INSERT INTO student_number (instance_id, fee_status_id, origin, aos_code, session, student_count)
                                        VALUES ({instance_id},
                                        '{row[headers['fee_status_id']]}',
                                        '{usage}',
                                        '{row[headers['aos_code']]}',
                                        {row[headers['session']]},
                                        {row[headers['student_count']]})"""
                        conn.execute(text(sql))
        if click.confirm("Confirm writing to database?"):
            trans.commit()
        else:
            trans.rollback()
