import click
from .configure import configure
from .display import display


@click.group()
@click.pass_obj
def settings(config):
    """ 
    Adjust local settings
    """
    pass


settings.add_command(configure)
settings.add_command(display)
