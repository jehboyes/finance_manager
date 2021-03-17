# pylint: disable=no-member
import click
from finance_manager.database.spec import f_set_costing, f_set
from finance_manager.database import DB
from sqlalchemy import and_


@click.command()
@click.argument("costc", type=str, nargs=1)
@click.argument("setcat", type=str, nargs=1)
@click.argument("acad_year", type=int, nargs=1)
@click.argument("costings", type=str, nargs=-1)
@click.pass_obj
def recharge(config, costc, setcat, acad_year, costings):
    """
    Recharge the given COSTC in SETCAT ACAD_YEAR to the given COSTINGS, 
    which must be supplied as <costc=proportion>. For example, 
    `fm recharge MA1600 BP2 2021 MA1500=20 MA1100=10` would apportion 67% to MA1500
    and 33% to MA1100 of the cost of MA1600 in 2021 BP2. 
    """
    # Get set ID
    config.set_section("planning")
    with DB(config=config) as db:
        session = db.session()
        s = session.query(f_set).filter(and_(f_set.costc == costc,
                                             f_set.acad_year == acad_year,
                                             f_set.set_cat_id == setcat)).one()
        prev_configs = session.query(f_set_costing)\
                              .filter(f_set_costing.set_id == s.set_id).all()
        if len(prev_configs) > 0:
            for conf in prev_configs:
                session.delete(conf)
            session.flush()
        for costing in costings:
            if costing[6] != "=":
                raise RuntimeError("Invalid costing " + costing)
            fsc = f_set_costing(set_id=s.set_id,
                                costc=costing[:6],
                                base_proportion=float(costing[7:]))
            session.add(fsc)
        session.commit()
