
from finance_manager.functions import _add_subcommands
import click


@click.group()
@click.pass_obj
def finance(config):
    """
    **Group** of finance-related commands.
    """
    pass


_add_subcommands(finance, __file__, __package__)
