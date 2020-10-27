# pylint: disable=no-member
import click
from .edit import edit
from .load import load
from .permissions import permissions
from .settings import settings

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
    config.obj = Config()
    config.obj.set_section("planning")


commands = [edit, load, permissions, settings]
for _ in commands:
    fm.add_command(_)
