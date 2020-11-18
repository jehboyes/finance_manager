# pylint: disable=no-member

from finance_manager.functions import _add_subcommands
import click


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


_add_subcommands(fm, __file__, __package__)
