import click
from .add import add as a
from .director import director as d


@click.group()
@click.pass_obj
def permissions(config):
    """
    Manage access to cost centres in the UI.
    """
    pass


permissions.add_command(a)
permissions.add_command(d)
