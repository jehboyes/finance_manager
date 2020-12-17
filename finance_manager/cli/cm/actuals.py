"""
Function for updating actuals from csv of HE IN YEAR COHORT DATA web report
"""

import csv
import click
from sqlalchemy import text
from finance_manager.functions import level_to_session, name_to_aos
from finance_manager.database import DB


@click.command()
@click.argument("acad_year", type=int)
@click.argument("filepath", type=str)
@click.pass_obj
def actuals(config, acad_year, filepath):
    """
    Use a csv export of HE In Year Cohort Data (saved at ``FILEPATH``) to update the 
    actuals in the curriculummodel database, in ``ACAD_YEAR``. 
    """
    entries = []
    with open(filepath, newline="") as file:
        rows = csv.reader(file)
        read = False
        for row in rows:
            # If a valid row to read from
            if len(row) > 0:
                if read:
                    entries.append((level_to_session(row[0]),
                                    row[2][0],
                                    name_to_aos(row[3])[0],
                                    int(row[9] or "0"))
                                   )
                if row[0] == "LevelOfStudy":
                    read = True
    n = 0
    if len(entries) != 0:
        config.set_section("cm")
        with DB(config=config) as db:
            sql = f"""INSERT INTO student_number_instance (acad_year, usage_id, lcom_username, costc)
                    OUTPUT INSERTED.instance_id VALUES({acad_year}, 'Actual', 'CL Interface', 'MA1100')"""

            with db._engine.begin() as transaction:
                instance_id = transaction.execute(text(sql)).fetchone()[0]
                entry_dict = {}
                for *key, count in entries:
                    key = tuple(key)
                    if key not in entry_dict:
                        entry_dict[key] = count
                    else:
                        entry_dict[key] = entry_dict[key] + count
                for key, count in entry_dict.items():
                    session, status, aos_code = key
                    if count > 0:
                        sql = f"""INSERT INTO student_number (instance_id, fee_status_id, origin, aos_code, session, student_count)
                                VALUES ({instance_id}, '{status}', 'Actual', '{aos_code}', {session}, {count})"""
                        transaction.execute(sql)
                        n += 1
    return n
