# pylint: disable=no-member
import click
import csv
import sys
from datetime import datetime
from finance_manager.database import DB
from finance_manager.database.spec import f_set, finance, finance_instance, account, entry_type
from finance_manager.functions import normalise_period
from sqlalchemy import and_, select, insert


@click.command()
@click.option("--acad_year", type=int)
@click.argument("set_cat_id", type=str)
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--unsigned", "-u", is_flag=True, help="Indicates that import data is unsigned (no negatives).")
@click.pass_obj
def load(config, acad_year, set_cat_id, unsigned, filepath):
    """
    Import Finance data.

    Load a csv with columns for costc, account, period & amount and
    load into ACAD_YEAR SET_CAT_ID. Target sets must exist.
    """
    headers = {}
    body = []
    valid_cols = ['account', 'period', 'amount', 'costc']
    if acad_year == None:
        valid_cols.append('acad_year')
    with open(filepath) as file:
        rows = csv.reader(file)
        for i, row in enumerate(rows):
            if i == 0:
                for j, col in enumerate(row):
                    headers.update({j: col})
                if acad_year != None:
                    headers.update({len(headers): 'acad_year'})
            else:
                if acad_year != None:
                    r = row + acad_year
                else:
                    r = row
                body.append({headers[k]: v for k, v in enumerate(r)
                             if headers[k] in valid_cols})
    if len(body[0]) != len(valid_cols):
        click.echo("Headers incorrect.")
        sys.exit()
    years = list(set([r['acad_year'] for r in body]))
    costcs = list(set([r['costc'] for r in body]))
    print(years)
    with DB(config=config) as db:
        con = db.con
        with con.begin() as transaction:
            # Need sets to map existing
            set_tbl = f_set.__table__
            sets = select([set_tbl.c.set_id,
                           set_tbl.c.set_cat_id,
                           set_tbl.c.acad_year,
                           set_tbl.c.costc]) \
                .where(and_(set_tbl.c.set_cat_id == set_cat_id,
                            set_tbl.c.costc.in_(costcs),
                            set_tbl.c.acad_year.in_(years)))
            # Create finance instance for each cost centre and year used
            mapping = {}
            for s in con.execute(sets).fetchall():
                stmt = insert(finance_instance.__table__) \
                    .values(created_by='CLI',
                            datestamp=datetime.now(),
                            set_id=s.set_id) \
                    .returning(finance_instance.__table__.c.instance_id)
                instance_id = con.execute(stmt).fetchall()[0].instance_id
                mapping[tuple([s.costc, s.acad_year])] = instance_id
            print(mapping)
            # Need account information for fixing balances
            acc = account.__table__
            et = entry_type.__table__
            accounts = select([acc.c.account, et.c.coefficient]) \
                .where(acc.c.default_balance == et.c.balance_type)
            account_bal = {
                a.account: (a.coefficient if not unsigned else 1)
                for a in con.execute(accounts)}
            # Create finacne row for each row in input, correcting ablances and period format
            inputs = []
            with click.progressbar(body, show_eta=True, show_percent=True, show_pos=True) as bar:
                for row in bar:
                    row_key = tuple([row['costc'], int(row['acad_year'])])
                    # Check costcentre isvalid for inclusion
                    if row_key not in mapping.keys():
                        click.echo(f"No set exists for {row_key}")
                        sys.exit()
                    # amounts stored as absolute rather than signed CR DB
                    inputs.append(dict(instance_id=mapping[row_key],
                                       account=int(row['account']),
                                       amount=float(row['amount'].replace(",", "")) *
                                       float(account_bal[row['account']]),
                                       period=normalise_period(row['period'])))
            con.execute(insert(finance.__table__), inputs)
            if click.confirm(f"Confirm writing {len(inputs)} finance records to DB?"):
                transaction.commit()
            else:
                transaction.rollback()
