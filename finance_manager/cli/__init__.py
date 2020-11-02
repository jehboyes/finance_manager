# pylint: disable=no-member
import click
from .database import database
from .load import load
from .permissions import permissions
from .settings import settings
from .finance import finance

from finance_manager.config import Config

pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.pass_context
def fm(config):
    """
    Finance Manager application.

    This application was designed to be a single point of reference 
    for administration tasks relating to the finance manager tool.
    """
    # Define config object to be passed to subcommands via click.pass_obj
    config.obj = Config()
    # Force the default configuration database to be planning
    config.obj.set_section("planning")


# Attach the rest of the click commands
commands = [database, load, permissions, settings, finance]
for _ in commands:
    fm.add_command(_)
