import click
import json
from utils.wallet import Wallet
from commands.issue_and_activate import handler


@click.command()

# config
@click.option('--network', default='rinkeby', help='Network the bounty will be funded on.')
@click.option('--secret', default='secrets.json', help='File that stores an HD wallet mnemonic.')
@click.option('--wallet-child', default=0, help='HD wallet generation.')
@click.option('--gas-price', default=5, help='Price in gWei paid per unit of gas.')

# required args
@click.argument('url')
@click.argument('amount', type=click.FLOAT)

@click.option('--token', default='ETH', help='The token that the bounty pays out to.')
@click.option('--token-address', default='0x0000000000000000000000000000000000000000', help='EIP20 token address the bounty pays out to.')

# metadata
@click.option('--github', prompt=True, help='Github username associated with bounty.')
@click.option('--title', prompt=True, help='The bounty\'s title.')
@click.option('--description', prompt=True, help='A description of what the bounty requires.')
@click.option('--keywords', prompt=True, help='Comma seperated keywords.')
@click.option('--experience', type=click.Choice(['beginner', 'intermediate', 'advanced']), prompt=True, help='Level of experience needed to complete this bounty.')
@click.option('--length', type=click.Choice(['hours', 'days', 'weeks', 'months']), prompt=True, help='Rough estimate on the amount of time needed to complete this bounty.')
@click.option('--type', type=click.Choice(['bug', 'feature', 'security', 'other']), prompt=True, help='The type of activity this bounty is funding.')

# default to empty
@click.option('--full-name', default='', prompt=False, help='')
@click.option('--notification-email', default='', prompt=False, help='')

# privacy
@click.option('--show-email/--hide-email', default=True)
@click.option('--show-name/--hide-name', default=True)

# short hand flags
@click.option('-b', 'experience', flag_value='beginner', help='Beginner experience level shortcut.')
@click.option('-i', 'experience', flag_value='intermediate', help='Intermediate experience level shortcut.')
@click.option('-a', 'experience', flag_value='advanced', help='Advanced experience level shortcut.')

@click.option('-h', 'length', flag_value='hours', help='Hours project length shortcut.')
@click.option('-d', 'length', flag_value='days', help='Days project length shortcut.')
@click.option('-w', 'length', flag_value='weeks', help='Weeks project length shortcut.')
@click.option('-m', 'length', flag_value='months', help='Months project length shortcut.')

#@click.option('-b', 'type', flag_value='bug')
@click.option('-f', 'type', flag_value='feature', help='Feature bounty type shortcut.')
@click.option('-s', 'type', flag_value='security', help='Security bounty type shortcut.')
@click.option('-o', 'type', flag_value='other', help='Other bounty type shortcut.')

@click.pass_context
def main(ctx, **kwargs):
    state = kwargs

    # load wallet from mnemonic for specified child
    wallet = Wallet.from_json(state.get('secret'), state.get('wallet_child'))

    state.update({ 'wallet': {
        'address': wallet.address,
        'private_key': wallet.private_key
    }})

    state.update({ 'keywords' : state.get('keywords').split(',') })

    handler(state)


if __name__ == '__main__':
    main()
# python3 src/cli.py a 1 -ahf --github color --title title --description description --keywords key,word
