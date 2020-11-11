# pylint: disable=no-member
import click
import csv
import sqlalchemy

from finance_manager.database import DB


@click.command()
@click.option("--path", type=click.Path(exists=False), help="Specify an output path")
@ click.argument("costc", nargs=-1, type=str)
@ click.pass_obj
def add(config, costc):
    """
    Returns all the claims in the year thus far from payclaim.

    Will restrict to the ``COSTC`` passed (several can be passed).
    """
    config.set_section("payclaim")
    with DB(config=config) as db:
        sql = f"""SELECT r.hourlyrate as hourly_rate,
            CASE WHEN r.ratetype = 'normal' THEN wt.short_type ELSE 'OTH' END as short_type,
            CASE WHEN m.mbCodeTitle = 'MC1911' THEN 'MC1922' ELSE m.mbCodeTitle END as costc,
            (c.durationhr*60+c.durationmin)*proportion/60 as claimed_hours,
            c.dateofclaim as date,
            CONCAT(month(c.dateofClaim), year(c.Dateofclaim)) as period
            FROM workrequest AS r
            INNER JOIN (SELECT worktypeUID, CASE WHEN worktypecode = "CAS" THEN "CAS"
                                                WHEN worktypemultiplier = 1.32 THEN "TEA"
                                                ELSE "OTH" END as short_type
                        FROM workrequest_worktype) AS wt ON r.worktypeUID = wt.worktypeUID
            INNER JOIN workrequest_claims AS c ON r.requestUID = c.requestUID
            INNER JOIN costings_mbcodes AS s ON r.costingUID = s.costingUID
            INNER JOIN costings_mbcodes_list AS m ON m.mbCodeUID = s.mbCodeUID
            """
        execution = db.con.execute(sql)
        keys = execution.keys()
        values = execution.fetchall()
    with open('payclaim_export.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_NONE)
        writer.writerow(keys)
        writer.writerows(values)
