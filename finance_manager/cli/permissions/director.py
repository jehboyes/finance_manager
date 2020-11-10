# pylint: disable=no-member
import click
import sqlalchemy
from sqlalchemy import and_
from finance_manager.database.spec import permission, cost_centre, directorate
from finance_manager.database import DB


@click.command()
@click.argument("login")
@click.argument("dirid")
@click.pass_obj
def director(config, login, dirid):
    """
    Set director. 

    Set ``LOGIN`` as the director for the directorate with ID ``DIRID``
    \f
    Parameters
    ----------
    config : Config
        Custom config object. 
    login : [type]
        [description]
    directorateid : [type]
        [description]
    """
    with DB(config=config) as db:
        s = db.session()
        try:
            d = s.query(directorate).filter(
                directorate.directorate_id == dirid).one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise ValueError(f"No such directorate {dirid}")
        d.director = login
        s.commit()
