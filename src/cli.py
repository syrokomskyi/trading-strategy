import click
from .command import run, optimize_ichimoku


@click.group()
def cli():
    """Crypto Trading Strategy Tester CLI"""
    pass


cli.add_command(run)

cli.add_command(optimize_ichimoku)

if __name__ == "__main__":
    cli()
