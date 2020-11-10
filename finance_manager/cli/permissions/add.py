# pylint: disable=no-member
import click
import sqlalchemy
from sqlalchemy import and_
from finance_manager.database.spec import permission, cost_centre, directorate
from finance_manager.database import DB


@click.command()
@click.option("--owner", help="Replace as cost centre owner instead of adding permissions", is_flag=True)
@click.argument("login")
@click.argument("costc", nargs=-1)
@click.pass_obj
def add(config, login, costc, owner):
    """
    Give a login cost centre access.

    Gives the specified ``LOGIN`` access to the specified ``COSTC`` (several can be listed)

    Parameters
    ----------
    login : str
        Office 365 login id (not including @...)
    costc : str
        6 character cost centre code
    """
    with DB(config=config) as db:
        s = db.session()
        for c in costc:
            if owner:
                try:
                    costc_record = s.query(cost_centre).filter(
                        cost_centre.costc == c).one()
                except sqlalchemy.orm.exc.NoResultFound:
                    raise ValueError(f"{c} not found in cost centres.")
                costc_record.owner = login
                s.query(permission).filter(and_(permission.login_365 == login,
                                                permission.costc == c)).delete()
            else:
                s.add(permission(costc=c, login_365=login))
        s.commit()
