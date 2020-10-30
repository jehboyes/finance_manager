# pylint: disable=no-member
import click

from finance_manager.database.db import DB
from finance_manager.database.spec import f_set, cost_centre


@click.command()
@click.option("--change_sn", help="Allow users to change student numbers", is_flag=True)
@click.argument("setcode")
@click.argument("acad_year", type=int)
@click.argument("curriculum")
@click.argument("sn_usage")
@click.pass_obj
def newset(config, acad_year, setcode, curriculum, sn_usage, change_sn):
    """
    Create new finance sets.

    Create a new set for each un-superceded cost centre, in ACAD_YEAR 
    with SETCODE, using the id of the CURRICULUM, and student number usage from 
    SN_USAGE. 

    \b
    Parameters
    ----------
    config : Config
        Custom config object.
    acad_year : int
        Academic year (calendar year commencing).
    setcode : str
        3 character set code ID.
    curriculum : int
        Curriculum ID (from Curriculum Model). 
    sn_usage : str
        Student Number Usage ID (from Curriculum Model). 
    """
    with DB(config=config) as db:
        s = db.session()
        # Get all valid cost centres
        cost_centres = s.query(cost_centre).filter(
            cost_centre.supercede_by == None).all()
        # Change the change_sn to a bit
        if change_sn:
            change_sn = 1
        else:
            change_sn = 0
        for costc in cost_centres:
            # Create a new set with given detail
            s.add(f_set(acad_year=acad_year,
                        set_cat_id=setcode,
                        curriculum_id=curriculum,
                        student_number_usage_id=sn_usage,
                        allow_student_number_change=change_sn,
                        costc=costc.costc))
        s.commit()
