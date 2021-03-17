# pylint: disable=no-member

import click
from finance_manager.database import DB
from finance_manager.database.spec import f_set
from curriculum_model.db.schema.views import CurriculumHours
from sqlalchemy.sql import select
from sqlalchemy import and_


@click.command()
@click.argument("setcat", type=str)
@click.argument("acad_year", type=int)
@click.pass_obj
def curriculum(config, setcat, acad_year):
    """
    Update the curriculum hours for the sets in the given SETCAT and ACAD_YEAR.
    """
    with DB(config=config) as db:  # Connect to curriculum db to get total hours
        session = db.session()
        sets = session.query(f_set).filter(and_(f_set.set_cat_id == setcat,
                                                f_set.acad_year == acad_year)).all()

        # Get connection variables for curriculum database
        config.set_section("cm")
        with DB(config=config) as cm_db:
            with click.progressbar(sets, show_eta=False,
                                   show_percent=True, item_show_func=_progress_print,
                                   label="Updating teaching hours") as bar:
                for s in bar:
                    # get curriculum hours
                    curriculum_select = select([CurriculumHours.c.hours]) \
                        .where(and_(CurriculumHours.c.usage_id == s.student_number_usage_id,
                                    CurriculumHours.c.curriculum_id == s.curriculum_id,
                                    CurriculumHours.c.costc == s.costc))
                    cur_hours = cm_db.con.execute(curriculum_select).fetchall()
                    if len(cur_hours) > 0:
                        s.curriculum_hours = cur_hours[0].hours
        session.flush()
        session.commit()


def _progress_print(s):
    if s is not None:
        return f"Processed {s.costc}"
