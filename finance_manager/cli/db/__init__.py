
from finance_manager.functions import _add_subcommands
import click


@click.group()
@click.pass_obj
def db(config):
    """
    **Group** of commands for generic db interaction and maintenance.  
    """
    pass


_add_subcommands(db, __file__, __package__)
