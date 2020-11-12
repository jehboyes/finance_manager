import click
from .claims import claims


@click.group()
@click.pass_obj
def export(config):
    """
    **Group** of commands for managing exports.
    """
    pass


export.add_command(claims)
