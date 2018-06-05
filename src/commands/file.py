import click
import json

@click.command()
@click.argument('filename', type=click.Path(exists=True))
def file(filename):
    data = {}

    try:
        with open(filename) as f:
            data.update(json.load(f))
    except:
        raise click.ClickException(f'Unable to open "{filename}". Please ensure it is a properly formatted JSON.')

    print(data)
