import click

from finance_manager.database.spec import f_set, f_set_cat
from finance_manager.database.db import DB
from finance_manager.config import Config

pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@pass_config
def fm(config):
    """
    Finance Manager application.

    This application was designed to be a single point of reference for administration tasks.
    """
    pass


@fm.group()
@pass_config
def sets(config):
    """
    Manage finance sets

    A set is a unique combination of cost centre, academic year, and type.
    Set type is detailed seperately in set code.
    """
    pass


@sets.group()
@pass_config
def codes(config):
    pass


@codes.command()
@click.argument('code')
@click.argument('description')
@pass_config
def add(config, code, description):
    """
    Add a new set code
    """
    new_code = f_set_cat(set_cat_id=code, description=description)
    with DB(config=config) as db:
        session = db.session()
        session.add(new_code)
        session.commit()


@fm.command()
def test():
    """
    Test connections and functionality
    """
    pass


@fm.group()
@pass_config
def settings(config):
    """
    Edit local configuration settings
    """


@settings.command()
@pass_config
def lst(config):
    """
    List available settings
    """
    print(config.section)
    print("-"*len(config.section))
    print(config.read_section())


@settings.command()
@click.option("--env", type=str)
@click.argument("pairs", nargs=-1)
@pass_config
def set(config, pairs, env):
    """
    Takes key:value pairs and adds/updates as neccesary
    """
    # change env if passed
    if env is not None:
        config.set_env(env)
    # And the actual values, if passed
    try:
        pairs = {p[0]: p[1] for p in [pair.split(":") for pair in pairs]}
        config.write(pairs)
    except:
        print("Set command failed. Check key:value argument(s) valid. ")


"""
Planned layout:

fm
    sets
        list ~list of sets, optional filters
        create ~ create new sets, accept all

    test ~ arguments: appviews, etc

"""
