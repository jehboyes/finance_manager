
from finance_manager.functions import _add_subcommands
import click


@click.group()
@click.pass_obj
def database(config):
    """
    **Group** of commands for editing data in the database. Will likely be broken up at some point. 
    """
    pass


_add_subcommands(database, __file__, __package__)
