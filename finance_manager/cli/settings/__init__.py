import click
from .configure import configure
from .display import display


@click.group()
@click.pass_obj
def settings(config):
    """ 
    **Group** of commands for adjusting local settings.
    """
    pass


settings.add_command(configure)
settings.add_command(display)
