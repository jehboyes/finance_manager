# pylint: disable=no-member
import click
import copy
from finance_manager.database import DB
from finance_manager.database.spec import nonp_other, pay_staff, pay_claim, f_set
from sqlalchemy import and_

lookup = {"staff": [pay_staff, "staff_line_id"],
          "claim": [pay_claim, "claim_id"],
          "nonp": [nonp_other, "nonp_id"]}


@click.command()
@click.argument("from_costc", type=str)
@click.argument("to_costc", type=str)
@click.argument("acad_year", type=int)
@click.argument("set_cat_id", type=str)
@click.argument("obj", type=click.Choice([k for k in lookup.keys()]))
@click.argument("cmd", type=click.Choice(["copy", "move"]))
@click.option("--replace", "-r", is_flag=True, help="Replace the current contents of the target set.")
@click.pass_obj
def move(config, from_costc, to_costc, acad_year, set_cat_id, obj, cmd, replace):
    """
    Move or copy instances between input tables. 

    Move OBJ to FROM_COSTC TO_COSTC in the SET_CAT_ID in ACAD_YEAR. 
    Operation is determined by CMD, one of: 

    - 'copy' for creating a copy, leaving the original unchanged. 
    - 'move' for changing the set, leaving no trace in the original. 
    """
    with DB(config=config) as db:
        s = db.session()
        lookup = {"staff": [pay_staff, "staff_line_id"],
                  "claim": [pay_claim, "claim_id"],
                  "nonp": [nonp_other, "nonp_id"]}
        db_obj = lookup[obj][0]
        original_set = s.query(f_set).filter(and_(f_set.costc == from_costc,
                                                  f_set.acad_year == acad_year,
                                                  f_set.set_cat_id == set_cat_id)).first()
        lines = s.query(db_obj).filter(
            db_obj.set_id == original_set.set_id).all()
        target_set = s.query(f_set).filter(and_(f_set.costc == to_costc,
                                                f_set.acad_year == acad_year,
                                                f_set.set_cat_id == set_cat_id)).first()
        replace_txt = ""
        if replace:
            target_preexist = s.query(db_obj).filter(
                db_obj.set_id == target_set.set_id)
            preexist_n = len(target_preexist.all())
            target_preexist.delete()
            replace_txt = f"(replacing {preexist_n} pre-existing rows) "
        # list of fields that will change, which is the PK (from the lookup) and the set_id
        change_fields = [lookup[obj][1], 'set_id']
        i = 0
        for old_line in lines:
            new_line = db_obj()
            i += 1
            # for each column, set the new val = old val if its not one of the change_fields
            for ax in old_line.__table__.columns:
                a = str(ax).split(".")[1]
                if a not in change_fields:
                    setattr(new_line, a, getattr(old_line, a))
            new_line.set_id = target_set.set_id
            if cmd == 'move':
                s.delete(old_line)
            s.add(new_line)
            s.flush()

        if click.confirm(f"Confirm {cmd} {i} {obj} lines {replace_txt} from {from_costc} to {to_costc} in {acad_year} {set_cat_id}?"):
            s.commit()
        s.rollback()
