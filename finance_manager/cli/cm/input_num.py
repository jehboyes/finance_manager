"""
Function for updating actuals from csv of HE IN YEAR COHORT DATA web report
"""

import csv
import click
from sqlalchemy import text
from finance_manager.functions import level_to_session, name_to_aos
from finance_manager.database import DB


@click.command()
@click.argument("filepath", type=str)
@click.argument("usage", type=str)
@click.pass_obj
def input_num(config, filepath, usage):
    """
    Input Student Numbers.

    Use a csv (saved at ``FILEPATH``) to update the student numbers with ``USAGE_ID`` 
    in the curriculum model database. 

    TODO Add validation checks for input, and try/excepts. 
    """
    # Dict of headers required and if string
    headers = {}
    years = {}
    with open(filepath, newline="") as file:
        rows = csv.reader(file)
        for i, col in enumerate(rows[0]):
            headers.update({col: i})
        for row in rows[1:]:
            years.update({row[headers['acad_year']]: 0})
    # instance for each year
    config.set_section("cm")
    with DB(config=config) as db:
        for acad_year in years:
            with db._engine.begin() as transaction:
                sql = f"""INSERT INTO student_number_instance (acad_year, usage_id, lcom_username, costc)
                    OUTPUT INSERTED.instance_id VALUES({acad_year}, {usage}, 'CL Interface', 'MA1100')"""
                instance_id = transaction.execute(text(sql)).fetchone()[0]
                click.echo(sql)
                for row in rows[1:]:
                    sql = f"""INSERT INTO student_number (instance_id, fee_status_id, origin, aos_code, session, student_count)
                                VALUES ({instance_id}, 
                                {row[headers['fee_status_id']]}, 
                                '{usage}', 
                                '{row[headers['aos_code']]}', 
                                {row[headers['session']]}, 
                                {row[headers['student_count']]})"""
                    click.echo(sql)
                    transaction.rollback()
