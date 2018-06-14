import click
import json
from commands.issue_and_activate import handler
from utils.wallet import Wallet
import utils.validators as validators


# load defaults from json
with open('funder/config/defaults.json') as f:
    defaults = json.load(f)

@click.command()

# config
@click.option('--network', default=lambda:defaults.get('network'), callback=validators.network, help='Network the bounty will be funded on.')
@click.option('--secret', default=lambda:defaults.get('secret_file'), callback=validators.secret, help='File that stores an HD wallet mnemonic.')
@click.option('--wallet-child', default=lambda:defaults.get('wallet_child'), help='HD wallet generation.')
@click.option('--gas-price', default=lambda:defaults.get('gas_price'), help='Price in gWei paid per unit of gas.')
@click.option('--gas-limit', default=lambda:defaults.get('gas_limit'), help='Amount of gas to be spent per transaction.')

# required args
@click.argument('url', callback=validators.url)
@click.argument('amount', type=click.FLOAT, callback=validators.amount)

@click.option('--token', default=lambda:defaults.get('token_symbol'), callback=validators.token, help='The token that the bounty pays out to.')
@click.option('--token-address', default=lambda:defaults.get('token_address'), help='EIP20 token address the bounty pays out to.')

# metadata
@click.option('--github', default=lambda:defaults.get('github'),
    prompt=True, help='Github username associated with bounty.')
@click.option('--title', prompt=True, help='The bounty\'s title.')
@click.option('--description', prompt=True, help='A description of what the bounty requires.')
@click.option('--keywords', prompt=True, help='Comma seperated keywords.')
@click.option('--experience', type=click.Choice(['beginner', 'intermediate', 'advanced']),
    prompt=True, help='Level of experience needed to complete this bounty.')
@click.option('--length', type=click.Choice(['hours', 'days', 'weeks', 'months']),
    prompt=True, help='Rough estimate on the amount of time needed to complete this bounty.')

# would like to make this `--bount-type` but waiting to resolve issue
# https://github.com/pallets/click/issues/1041
@click.option('--type', type=click.Choice(['bug', 'feature', 'security', 'other']),
    prompt=True, help='The type of activity this bounty is funding.')

@click.option('--project-type', default=lambda:defaults.get('project_type'),
    type=click.Choice(['traditional', 'contest', 'cooperative']),
    prompt=False, help='How other will interact on this bounty.')
@click.option('--permission-type', default=lambda:defaults.get('permission_type'),
    type=click.Choice(['permissionless', 'approval']),
    prompt=False, help='Whether a bounty needs to approve workers.')


@click.option('--full-name', default=lambda:defaults.get('full_name'), prompt=False, help='')
@click.option('--notification-email', default=lambda:defaults.get('notification_email'), prompt=False, help='')

# privacy
@click.option('--show-email/--hide-email', default=lambda:defaults.get('show_email'))
@click.option('--show-name/--hide-name', default=lambda:defaults.get('show_name'))

# short hand flags
# TODO make these arguments hidden when click 7.0 comes out https://github.com/pallets/click/pull/500
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
    try:
        wallet = Wallet.from_json(state.get('secret'), state.get('wallet_child'))
    except:
        raise click.UsageError('unable to initialize wallet, ensure that secrets.json is set correctly.')

    state.update({ 'wallet': {
        'address': wallet.address,
        'private_key': wallet.private_key
    }})

    # add a little padding
    print('')

    # fund bounty
    handler(state)


if __name__ == '__main__':
    main()
