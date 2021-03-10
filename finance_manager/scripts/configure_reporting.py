# pylint: disable=no-member
from finance_manager.database.spec import report_cat_config, cost_centre, account
from finance_manager.database import DB
from finance_manager.config import Config
from sqlalchemy import select, and_, or_, not_


def configure_reporting():
    """Populates the reporting_cat_config
    """
    rc = report_cat_config.__table__
    cc = cost_centre.__table__
    a = account.__table__
    config = Config()
    config.verbose = True
    with DB(config=config) as db:
        with db._engine.begin() as con:
            statements = []
            # List of pay accounts for reference
            pay_accounts = con.execute(
                select([a.c.account]).where(or_(and_(a.c.account >= 2000,
                                                     a.c.account < 3000),
                                                a.c.summary_code == 401,
                                                a.c.summary_code == 405)))
            pay_accounts = [a.account for a in pay_accounts]
            # Non pay accounts for reference
            nonp_accounts = con.execute(
                select([a.c.account]).where(and_(a.c.summary_code >= 301,
                                                 a.c.summary_code < 400)))
            nonp_accounts = [a.account for a in nonp_accounts]
            # set existing to Null
            statements.append(rc.update()
                                .values(rep_cat_a_id=None))
            # Other staff costs
            statements.append(rc.update()
                                .where(and_(rc.c.account.in_(pay_accounts)))
                                .values(rep_cat_a_id='OSO'))
            # academic pay
            cc_academic = "".join("MA1700,MC1610,MC1700,MC1810,MC1814,MC1820,MC1824," +
                                  "MC1825,MC1827,MC1830,MC1910,MC1912,MC1920,MC1922," +
                                  "MC1923,MC1924,MC1925,MC2000,MC2010,MC2923").split(",")
            statements.append(rc.update()
                                .where(rc.c.costc.in_(cc_academic))
                                .where(rc.c.account.in_(pay_accounts))
                                .values(rep_cat_a_id='ACS'))
            # facilities staff costs
            cc_facility = "MB1100,MC1400,MC1430,MB1410".split(",")
            statements.append(rc.update()
                                .where(and_(rc.c.costc.in_(cc_facility),
                                            rc.c.account.in_(pay_accounts),
                                            or_(rc.c.costc != 'MB1100',  # Internal rent appears on this combo
                                                rc.c.account != 4371)))
                                .values(rep_cat_a_id='OSF'))
            # Academic support staff costs
            cc_support = con.execute(
                select([cc.c.costc]).where(((cc.c.directorate_id == "Q") &
                                            (cc.c.costc != "MC1400")) |
                                           (cc.c.costc.in_(['MA1420', 'MA1450', 'MC1410']))))
            cc_support = [c.costc for c in cc_support]
            statements.append(rc.update()
                                .where(and_(rc.c.costc.in_(cc_support),
                                            rc.c.account.in_(pay_accounts)))
                                .values(rep_cat_a_id='OSA'))
            # Other operating
            statements.append(rc.update()
                                .where(rc.c.account.in_(nonp_accounts))
                                .values(rep_cat_a_id='OEO'))
            # Academic operating costs
            statements.append(rc.update()
                                .where(and_(rc.c.costc.in_(cc_academic),
                                            rc.c.account.in_(nonp_accounts)))
                                .values(rep_cat_a_id="OEA"))
            # academic support operating
            statements.append(rc.update()
                                .where(and_(rc.c.costc.in_(cc_support),
                                            rc.c.account.in_(nonp_accounts)))
                                .values(rep_cat_a_id='OES'))
            # facilities operating
            depr_accounts = con.execute(
                select([a.c.account]).where(a.c.summary_code == 402))
            depr_accounts = [a.account for a in depr_accounts]
            statements.append(rc.update()
                                .where(or_(and_(rc.c.costc.in_(cc_facility),
                                                rc.c.account.in_(nonp_accounts)),
                                           rc.c.account.in_(
                                               [4220, 4221, 3310, 4955]),
                                           rc.c.account.in_(depr_accounts),
                                           and_(rc.c.costc == 'MB1100',  # Internal rent appears on this combo
                                                rc.c.account == 4371)))
                                .values(rep_cat_a_id='OEF'))
            # income
            statements.append(rc.update()
                                .where(or_(rc.c.account < 2000,
                                           rc.c.account == 4361))
                                .values(rep_cat_a_id='OIO'))
            statements.append(rc.update()
                                .where(rc.c.account == 1100)
                                .values(rep_cat_a_id='GGG'))
            statements.append(rc.update()
                                .where(and_(rc.c.account >= 1240, rc.c.account <= 1245))
                                .values(rep_cat_a_id='HFH'))
            # internal
            statements.append(rc.update()
                                .where(or_(rc.c.account.in_([4370, 4360])))
                                .values(rep_cat_a_id=None))

            for stmt in statements:
                con.execute(stmt)
            remaining_nulls = con.execute(select([rc.c.account, rc.c.costc])
                                          .where(rc.c.rep_cat_a_id == None)
                                          .where(not_(rc.c.account.in_([4370, 4360]))))
            remaining_nulls = [(a, b) for a, b in remaining_nulls]
            if len(remaining_nulls) != 0:
                raise RuntimeError('Null config rows remaining.')
            else:
                print(
                    'No non-internal NULL configurations remaining (process successful).')


if __name__ == "__main__":
    configure_reporting()
