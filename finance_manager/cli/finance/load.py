# pylint: disable=no-member
import click
import csv
import sys
from datetime import datetime
from finance_manager.database import DB
from finance_manager.database.spec import f_set, finance, finance_instance, account, entry_type
from finance_manager.functions import normalise_period
from sqlalchemy import and_


@click.command()
@click.argument("acad_year", type=int)
@click.argument("set_cat_id", type=str)
@click.argument("filepath", type=click.Path(exists=True))
@click.pass_obj
def load(config, acad_year, set_cat_id, filepath):
    """
    Import Finance data.

    Load a csv with columns for costc, account, period & amount and
    load into ACAD_YEAR SET_CAT_ID. Target sets must exist.
    """
    headers = {}
    body = []
    valid_cols = ['costc', 'account', 'period', 'amount']
    with open(filepath) as file:
        rows = csv.reader(file)
        for i, row in enumerate(rows):
            if i == 0:
                for j, col in enumerate(row):
                    headers.update({j: col})
            else:
                body.append({headers[k]: v for k, v in enumerate(row)
                             if headers[k] in valid_cols})
    if len(body[0]) != len(valid_cols):
        click.echo("Headers incorrect.")
        sys.exit()
    with DB(config=config) as db:
        sess = db.session()
        # Need sets to map existing
        sets = sess.query(f_set).filter(and_(f_set.set_cat_id == set_cat_id,
                                             f_set.acad_year == acad_year)).all()
        costc_map = {}
        # Create finance instance for each (cost centre)
        for s in sets:
            inst = finance_instance(created_by='CLI', datestamp=datetime.now(),
                                    set_id=s.set_id)
            sess.add(inst)
            sess.flush()
            costc_map[s.costc] = inst.instance_id
        # Need account information for fixing balances
        accounts = sess.query(account, entry_type).filter(
            account.default_balance == entry_type.balance_type).all()
        account_bal = {
            a.account.account: a.entry_type.coefficient for a in accounts}
        # Create finacne row for each row in input, correcting ablances and period format
        inputs = []
        for row in body:
            # Check costcentre isvalid for inclusion
            if row['costc'] not in costc_map.keys():
                click.echo(f"No set exists for {row['costc']}")
                sys.exit()
            # amounts stored as absolute rather than signed CR DB
            record = finance(instance_id=costc_map[row['costc']],
                             account=row['account'],
                             amount=float(row['amount'].replace(",", "")) *
                             float(account_bal[row['account']]),
                             period=normalise_period(row['period']))
            inputs.append(record)
        if click.confirm(f"Confirm writing {len(inputs)} finance records to DB?"):
            sess.bulk_save_objects(inputs)
            sess.commit()
