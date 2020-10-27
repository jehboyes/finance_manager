import click
from finance_manager.cli import pass_config


@click.command
@click.argument("login")
@click.argument("costc", nargs=-1)
def add (login, costc):
    """
    Give a login cost centre access.
    
    Gives the specified LOGIN access to the specified COSTC (several can be listed) 
    """