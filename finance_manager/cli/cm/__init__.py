
from finance_manager.functions import _add_subcommands
import click


@click.group()
@click.pass_obj
def cm(config):
    """
    **Group** of commands for interacting with the Curriculum Model. 
    """
    pass


_add_subcommands(cm, __file__, __package__)
