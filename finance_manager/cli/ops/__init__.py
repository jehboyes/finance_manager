
from finance_manager.functions import _add_subcommands
import click


@click.group()
@click.pass_obj
def ops(config):
    """
    **Group** of commands for admin-level maintenance operations. 
    """
    pass


_add_subcommands(ops, __file__, __package__)
