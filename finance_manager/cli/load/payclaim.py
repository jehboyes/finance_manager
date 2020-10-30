# pylint: disable=no-member
import click
import progressbar
from sqlalchemy import text, and_
from finance_manager.database.db import DB
from finance_manager.database.spec import f_set, pay_claim
from finance_manager.functions import period_to_month, periods


@click.command()
@click.argument("target_cat")
@click.argument("acad_year", type=int)
@click.argument("period", type=int)
@click.pass_obj
def payclaim(config, target_cat, acad_year, period):
    """
    Import claimed hours from payclaim.

    Creates pay claim 'actual' lines using the hours claimed in Pay Claim.
    Adds lines to TARGET_CAT sets in ACAD_YEAR up to and including the given PERIOD.
    Uses TARGET_CAT and ACAD_YEAR to find cost centre -> set_id mappings.

    Parameters
    ----------
    config
        Custom configuration object.
    target_cat
        Set category ID of the target sets
    base_cat
        Set category ID of the sets to used to fill future periods
    acad_year
        Academic year (calendar year commencing)
    """
    # Pay claim doesn't know periods, so create a list of month&year
    periods_to_date = [(n, *period_to_month(n, acad_year))
                       for n in periods(period)]
    period_withmonth = ([(n, str(m)+str(y))
                         for n, m, y in periods_to_date])
    period_filter = ", ".join([m for n, m in period_withmonth])
    pivot_periods = ", \n".join([
        f"""SUM(IF(period = {m},claimed_hours,NULL)) AS p{n}""" for n, m in period_withmonth])
    # Using SQL rather than build mappings for pay claim database
    inner_sql = f"""SELECT SUM(r.hourlyrate*(c.durationhr*60+c.durationmin))/SUM(c.durationhr*60+c.durationmin) as avg_hourly_rate,
            CASE WHEN r.ratetype = 'normal' THEN wt.short_type ELSE 'OTH' END as short_type, 
            CASE WHEN m.mbCodeTitle = 'MC1911' THEN 'MC1922' ELSE m.mbCodeTitle END as costc,
            SUM(c.durationhr*60+c.durationmin*proportion)/60 as claimed_hours,
            COUNT(c.requestUID) as claim_count, 
            CONCAT(month(c.dateofClaim), year(c.Dateofclaim)) as period
            FROM workrequest AS r
            INNER JOIN (SELECT worktypeUID, CASE WHEN worktypecode = "CAS" THEN "CAS"
                                                WHEN worktypemultiplier = 1.32 THEN "TEA"
                                                ELSE "OTH" END as short_type
                        FROM workrequest_worktype) AS wt ON r.worktypeUID = wt.worktypeUID
            INNER JOIN workrequest_claims AS c ON r.requestUID = c.requestUID
            INNER JOIN costings_mbcodes AS s ON r.costingUID = s.costingUID
            INNER JOIN costings_mbcodes_list AS m ON m.mbCodeUID = s.mbCodeUID
            GROUP BY c.worktypeMultiplier, m.mbCodeTitle,month(c.dateofClaim) , year(c.Dateofclaim), wt.short_type, r.ratetype
            """

    sql = f"""SELECT SUM(avg_hourly_rate*claimed_hours)/SUM(claimed_hours) as rate, 
                CONCAT(SUM(claim_count), ' claims submitted') as description, short_type as claim_type_id, costc, 
                {pivot_periods} 
                FROM ({inner_sql}) as x 
                WHERE period in ({period_filter})
                GROUP BY short_type, costc"""
    # Convert to SQL Alchemy statement
    sql = text(sql)
    # Setup config to use payclaim credentials
    config.set_section("payclaim")
    with DB(config=config) as db:
        click.echo(f"Reading from Payclaim database... ", nl=False)
        execution = db.con.execute(sql)
        keys = execution.keys()
        values = execution.fetchall()
        click.echo("Complete.")
    claim_data = [{k: v for k, v in zip(keys, row)} for row in values]
    config.set_section("planning")
    with DB(config=config) as db:
        session = db.session()
        # Query of f_sets relevant
        f_set_ids = session.query(f_set.set_id, f_set.costc).filter(and_(f_set.acad_year == acad_year,
                                                                         f_set.set_cat_id == target_cat)).all()
        costc_dict = {c: s for s, c in f_set_ids}
        insert_records = []
        for row in claim_data:
            row["set_id"] = costc_dict[row["costc"]]
            row.pop("costc")
            insert_records.append(row)
        click.echo("Committing... ", nl=False)
        session.bulk_insert_mappings(pay_claim, insert_records)
        session.commit()
        click.echo("Complete.")
