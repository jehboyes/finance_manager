# pylint: disable=no-member
import click
import csv
import sys
from datetime import datetime
from finance_manager.database import DB
from finance_manager.database.spec import f_set, transaction, account, entry_type
from finance_manager.functions import normalise_period
from sqlalchemy import and_


@click.command()
@click.argument("acad_year", type=int)
@click.argument("set_cat_id", type=str)
@click.argument("filepath", type=click.Path(exists=True))
@click.pass_obj
def transactions(config, acad_year, set_cat_id, filepath):
    """
    Import and clean Finance transactions.

    Removes reversing journals and reveresing VAT charges from transaction lists.
    """
    headers = {}
    body = []
    # read into list and check headers match
    valid_cols = ['costc', 'account', 'period', 'amount', 't',
                  'tt', 'trans.date', 'ap/ar id (t)', 'text', 'transno']
    with open(filepath, newline="", encoding='utf8', errors='ignore') as file:
        rows = csv.reader(file)
        for i, row in enumerate(rows):
            if i == 0:
                for j, col in enumerate(row):
                    headers.update({j: col.lower()})
            else:
                body.append({headers[k]: v if len(v) > 0 else None for k, v in enumerate(row)
                             if headers[k] in valid_cols})
    if len(body[0]) != len(valid_cols):
        click.echo("Headers incorrect: " + "|".join(list(body[0].keys())))
        sys.exit()
    # Clean, and remove zero-sum transaction & account combos
    idrow_dict = {}
    period_dict = {}
    for row in body:
        key = _row_key(row)
        row['period'] = normalise_period(row['period'])
        row['amount'] = row['amount'].replace(",", "")
        date_components = [int(c) for c in row['trans.date'].split("/")[::-1]]
        row['trans.date'] = datetime(*date_components)
        idrow_dict.update({key: idrow_dict.get(key, 0) + float(row['amount'])})
        period_dict.update({row['transno']: row['period']})
    body = [row for row in body if idrow_dict[_row_key(row)] != 0]
    to_remove = {}
    with click.progressbar(idrow_dict.items(), label="Detecting reversing journals") as bar:
        for i, iv in bar:
            for j, jv in idrow_dict.items():
                if not to_remove.get(j, False):
                    criteria = [
                        # The cost centres and accounts match
                        i[-11:] == j[-11:],
                        # They sum to zero
                        iv + jv == 0,
                        # the transaction IDs are chronolgically close
                        abs(int(i[:8]) - int(j[:8])) <= 50,
                        # They are at most one period apart
                        abs(period_dict[i[:8]] - period_dict[j[:8]]) <= 1
                    ]
                    if all(criteria):
                        to_remove.update({j: True})
    body = [row for row in body if not to_remove.get(_row_key(row), False)]

    # Detect and remove reversing journals by checking other transactions for zero sum

    with DB(config=config) as db:
        sess = db.session()
        # Need sets to map existing
        filter_clause = and_(f_set.set_cat_id == set_cat_id,
                             f_set.acad_year == acad_year)
        sets = sess.query(f_set).filter(filter_clause)
        costc_map = {s.costc: s.set_id for s in sets.all()}
        # Clear existing transactions
        click.echo("Clearing set's existing transactions...", nl=False)
        trans = sess.query(transaction).join(f_set).filter(filter_clause)
        for tran in trans:
            sess.delete(tran)
        sess.flush()
        click.echo("Complete. ")
        # Need account information for fixing balances
        accounts = sess.query(account, entry_type).filter(
            account.default_balance == entry_type.balance_type).all()
        account_bal = {
            a.account.account: a.entry_type.coefficient for a in accounts}
        inputs = []
        for row in body:
            tran = transaction(set_id=costc_map[row['costc']],
                               transaction_id=row['transno'],
                               account=row['account'],
                               period=row['period'],
                               status_id=row['t'],
                               type_id=row['tt'],
                               dt=row['trans.date'],
                               supplier_name=row['ap/ar id (t)'],
                               description=row['text'],
                               amount=float(row['amount']) *
                               float(account_bal[row['account']])
                               )
            inputs.append(tran)
        if click.confirm(f"Confirm writing {len(inputs)} transactions to DB?"):
            click.echo("Writing to DB... ", nl=False)
            sess.bulk_save_objects(inputs)
            sess.commit()
            click.echo("Complete.")
        else:
            sess.rollback()


def _row_key(d):
    return "|".join([d['transno'], d['costc'], d['account']])
