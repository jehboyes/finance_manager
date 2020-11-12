# pylint: disable=no-member
import click
from .database import database
from .load import load
from .permissions import permissions
from .settings import settings
from .finance import finance
from .export import export 

from finance_manager.config import Config

pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.pass_context
def fm(config):
    """
    Entry point for the CLI. 

    Just calling ``fm`` can't actually do anything, besides bringing up a help message. Programmatically, 
    ``fm`` creates the instance of the configuration object nad defaults it to use the 'planning' section. 
    This is the point at which a config.ini file is referenced/created in the parent directory, which is documented 
    in the config section.  


    """
    # Define config object to be passed to subcommands via click.pass_obj
    config.obj = Config()
    # Force the default configuration database to be planning
    config.obj.set_section("planning")


# Attach the rest of the click commands
commands = [database, load, permissions, settings, finance, export]
for _ in commands:
    fm.add_command(_)
