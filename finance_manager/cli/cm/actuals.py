# pylint: disable=no-member
"""
Function for updating actuals from csv of HE IN YEAR COHORT DATA web report
"""

import csv
import click
from sqlalchemy import text
from finance_manager.functions import level_to_session, name_to_aos
from finance_manager.database import DB
from curriculum_model.db.schema import SNInstance, SN
from datetime import datetime
from collections import defaultdict


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
    if len(entries) != 0:
        config.set_section("cm")
        with DB(config=config) as db:
            session = db.session()
            instance = SNInstance(acad_year=acad_year,
                                  usage_id='Actual',
                                  input_datetime=datetime.now(),
                                  lcom_username="CLI",
                                  surpress=False,
                                  costc='MA1100')
            session.add(instance)
            session.flush()
            entry_dict = defaultdict(int)
            # condense entries to satisfy primary key
            for *key, count in entries:
                key = tuple(key)
                entry_dict[key] += count
            for key, count in entry_dict.items():
                session, status, aos_code = key
                if count > 0:
                    num = SN(instance_id=instance.instance_id,
                             fee_status_id=status,
                             origin='Actual',
                             aos_code=aos_code,
                             session=session,
                             student_count=count)
                    session.add(num)
            if click.confirm("Confirm write to DB?"):
                session.commit()
            else:
                session.rollback()
