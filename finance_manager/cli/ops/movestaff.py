# pylint: disable=no-member
import click
import copy
from finance_manager.database import DB
from finance_manager.database.spec import pay_staff, f_set
from sqlalchemy import and_


@click.command()
@click.argument("staff_line_id", type=int)
@click.argument("costc", type=str)
@click.argument("cmd", type=click.Choice(["copy", "move", "propose"]))
@click.option("--set_cat_id", type=str, help="Moves to the set in a different category.")
@click.option("--acad_year", type=int, help="Moves to the set in a different year.")
@click.pass_obj
def movestaff(config, staff_line_id, costc, cmd, set_cat_id, acad_year):
    """
    Move an input_pay_staff line. 

    Move STAFF_LINE_ID to the set with COSTC. 
    Operation is determined by CMD, one of: 

    - ``copy`` for creating a copy, leaving the original unchanged. 
    - ``move`` for changing the set, leaving no trace in the original. 
    - ``propose`` for creating a copy, and marking the original as pre-change. 
    """
    with DB(config=config) as db:
        s = db.session()
        original_post = s.query(pay_staff).filter(
            pay_staff.staff_line_id == staff_line_id).first()
        original_set = s.query(f_set).filter(
            f_set.set_id == original_post.set_id).first()
        target_set = s.query(f_set).filter(and_(
            f_set.acad_year == original_set.acad_year,
            f_set.set_cat_id == original_set.set_cat_id,
            f_set.costc == costc)).first()
        new_post = pay_staff()
        change_fields = ['staff_line_id', 'set_id']
        for ax in original_post.__table__.columns:
            a = str(ax).split(".")[1]
            if a not in change_fields:
                setattr(new_post, a, getattr(original_post, a))
        new_post.set_id = target_set.set_id
        if cmd == 'move':
            s.delete(original_post)
        elif cmd == 'propose':
            original_post.post_status_id = 'OLD'
            new_post.post_status_id = 'PRC'
        s.add(new_post)
        s.flush()
        if click.confirm(f"Confirm {cmd} {new_post.name} to {target_set.costc}?"):
            s.commit()
        s.rollback()
