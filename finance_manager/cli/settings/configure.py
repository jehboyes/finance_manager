# pylint: disable=no-member
import click


@click.command()
@click.option("--env", type=str, help="Use this to change the environment")
@click.argument("pairs", nargs=-1)
@click.pass_obj
def configure(config, pairs, env):
    """
    Takes key:value ``PAIRS`` and adds/updates as neccesary.
    """
    # change env if passed
    if env is not None:
        config.set_env(env)
    # And the actual values, if passed
    try:
        pairs = {p[0]: p[1] for p in [pair.split(":") for pair in pairs]}
        config.write(pairs)
    except:
        print("Set command failed. Check key:value argument(s) valid. ")
