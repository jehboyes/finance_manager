# pylint: disable=no-member

import click
from finance_manager.database.db import DB
from finance_manager.database.spec import f_set


@click.command()
@click.option("--costc", type=str, help="Limit to a cost centre")
@click.option("--set_id", type=int, help="Limit to an individual set")
@click.option("--cat", type=str, help="Limit to a set category")
@click.option("--year", type=int, help="Limit to an academic year")
@click.pass_obj
def curriculum(config, costc, set_id, cat, year):
    """Update the curriculum hours for all sets.

    Use the options to restrict which sets are updated
    """
    config.set_section("cm")  # Get connection variables for curriculum database
    with DB(config=config) as db:  # Connect to curriculum db to get total hours
        hours = db.con.execute(
            "SELECT curriculum_id, costc, hours FROM vCurriculumEnrolsForAppTotal").fetchall()
    hours = {(x[0], x[1]): x[2] for x in hours}
    config.set_section("planning")  # Connection variables for planning database
    with DB(config=config) as db:  # Connect to planning DB
        session = db.session()
        set_list = session.query(f_set)
        if set_id is not None:
            print("check")
            set_list = set_list.filter_by(set_id=set_id)
        else:  # Else at this point used because set_id overwrites other filters
            if costc is not None:
                set_list = set_list.filter_by(costc=costc)
            if cat is not None:
                set_list = set_list.filter_by(set_cat_id=cat)
            if year is not None:
                set_list = set_list.filter_by(acad_year=year)
        sets = set_list.all()
        for s in sets:
            s.curriculum_hours = hours.get((s.curriculum_id, s.costc), 0)
        session.commit()
