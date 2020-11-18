
from finance_manager.functions import _add_subcommands
import click


@click.group()
@click.pass_obj
def settings(config):
    """ 
    **Group** of commands for adjusting local settings.
    """
    pass


_add_subcommands(settings, __file__, __package__)
