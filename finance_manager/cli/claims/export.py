# pylint: disable=no-member
import click
import csv
import sqlalchemy

from finance_manager.database import DB


@click.command()
@click.option("--path", type=click.Path(exists=False), help="Specify an output path.")
@click.option("--seperate", is_flag=True, help="Output each cost centre to a seperate file.")
@click.argument("costc", nargs=-1, type=str)
@click.pass_obj
def export(config, costc, seperate, path):
    """
    Returns all the claims in the year thus far from payclaim.

    Will restrict to the ``COSTC`` passed (several can be passed). Lack of indexing within the payclaim database makes
    executing a single SQL statement impractical, and potentially disruptive to the running of the system, hence the code is more involved.
    """
    config.set_section("payclaim")
    with DB(config=config) as db:
        sql = f"""SELECT 
                    CASE WHEN m.mbCodeTitle = 'MC1911' THEN 'MC1922' ELSE m.mbCodeTitle END as costc,
                    r.userUID, r.hourlyrate as hourly_rate, r.title, r.notes, c.notes as claim_notes, 
                    CASE WHEN r.ratetype = 'normal' THEN wt.short_type ELSE 'OTH' END as short_type,
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
        if len(costc) > 0:
            costc_str = ", ".join([f"'{c}'" for c in costc])
            sql += f"\rWHERE m.mbcodetitle IN ({costc_str})"
        execution = db.con.execute(sql)
        keys = execution.keys()
        values = execution.fetchall()
        # Get a dictionary of users. Much Quicker than doing it in the database!
        user_keys = ["staffid", "firstname", "lastname"]
        user_dict = _get_dict(db, "users", "userUID", user_keys)
    keys = keys + user_keys
    with open('payclaim_export.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        writer.writerow(keys)
        for row in values:
            try:
                row = list(row)
                row = row + list(user_dict[row[1]])
            #    row = [r.replace("\\u200b", " ") for r in row if isinstance(r, str)]
                writer.writerow(row)
            except Exception as e:
                print(row)
                print(e)
                raise RuntimeError


def _get_dict(db, table, keys, values=[]):
    """
    Returns a dictionary for the given table.

    Workaround for dealing with unindexed tables.
    """
    if len(list(keys)) > 1:
        key = tuple(keys)
    if not isinstance(values, list):
        values = [values]
    select_fields = ", ".join([keys] + values)
    sql = f"SELECT {select_fields} FROM {table}"
    results = db.con.execute(sql).fetchall()
    d = {}
    for result in results:
        d[result[0]] = result[1:]
    return d
