
from finance_manager.functions import _add_subcommands
import click
from .export import export
from .load import load


@click.group()
@click.pass_obj
def claims(config):
    """
    **Group** of commands for managing exports.
    """
    pass


_add_subcommands(claims, __file__, __package__)
