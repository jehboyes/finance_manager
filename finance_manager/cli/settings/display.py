import click


@click.command()
@click.pass_obj
def display(config):
    """
    List configuration settings.
    """
    section = config.section
    click.echo("Environment: ")
    click.echo(section)
    click.echo("-"*len(section))
    click.echo(config.read_section())
