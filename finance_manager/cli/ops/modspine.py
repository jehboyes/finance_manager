# pylint: disable=no-member
import click

from finance_manager.database import DB
from finance_manager.database.spec import spine
from sqlalchemy.orm import aliased
from sqlalchemy import and_
from tabulate import tabulate


@click.command()
@click.argument("targetset", type=str)
@click.argument("targetyear", type=int)
@click.argument("change", type=float)
@click.option("--source", type=(str, int), default=(None, None), help=("Base change on a specified set and year."))
@click.pass_obj
def modspine(config, targetset, targetyear, change, source):
    """
    Alter existing spine point values. 

    Alters the value of the spine points in TARGETSET TARGETYEAR by 1 + CHANGE (e.g. to effect a 3% decrease, pass -0.03). 
    If SOURCESET and SOURCEYEAR are passed (via source option), the percentage change will be applied to those instead. 
    """
    if source != (None, None):
        sourceset, sourceyear = source
        if not(sourceset == None and sourceyear == None) and not(sourceset != None and sourceyear != None):
            click.echo(
                "If passing a source, both a set cat and year must be passed.")
            return
    with DB(config=config) as db:
        s = db.session()
        change_sp = s.query(spine).filter(and_(spine.acad_year == targetyear,
                                               spine.set_cat_id == targetset))
    if source != (None, None):
        source_sp = s.query(spine).filter(and_(spine.acad_year == sourceyear,
                                               spine.set_cat_id == sourceset))
        source_sp = {r.spine: r.value for r in source_sp.all()}
        for sp in change_sp:
            sp.value = float(source_sp[sp.spine])*(1+change)
    else:
        for sp in change_sp:
            sp.value = float(sp.value)*(1+change)
    s.flush()
    s.commit()
