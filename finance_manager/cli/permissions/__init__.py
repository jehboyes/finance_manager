
from finance_manager.functions import _add_subcommands
import click


@click.group()
@click.pass_obj
def permissions(config):
    """
    **Group** of commands for managing access to cost centres in the UI.
    """
    pass


_add_subcommands(permissions, __file__, __package__)
