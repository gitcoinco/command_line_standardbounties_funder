from click import UsageError
from clint.textui import puts, colored
from eth_utils import to_checksum_address
from web3.exceptions import BadFunctionCallOutput

from config.web3 import web3_client
from config.contracts import getBountiesContract, getTokenContract
from utils.token_list import name_to_token


def getTokenInfo(state):
    # get token address and decimal places from symbol
    info = name_to_token(state.get('token'))

    # user wants to use custom token if address != 0x0
    if(state.get('token_address') != '0x0000000000000000000000000000000000000000'):

        try:
            token = getTokenContract(state.get('network'), to_checksum_address(state.get('token_address')))
        except BadFunctionCallOutput:
            raise UsageError('there doesn\'t seem to be a token at that address...')

        print('Getting token info... ', end='', flush=True)

        info.update({
            #'name' : t.functions.name().call()),
            'addr': state.get('token_address'),
            'name': token.functions.symbol().call(),
            'decimals': token.functions.decimals().call()
        })

        puts(colored.green('done.'))

    # fail if no token info was provided
    if(not info):
        print(f'Error {data.get("tokenName")} is not supported.')
        exit(1)

    return {
        'token': info.get('name'),
        'token_address': info.get('addr'),
        'token_decimals': int(info.get('decimals')),

        # set amount to correct unit by multiplying the human-readable unit by
        # the number of decimals.
        'amount': int(state.get('amount') * pow( 10, int(info.get('decimals'))) )
    }

def approveTokenTransfer(state):
    web3 = web3_client(state.get('network'))
    bountiesContract = getBountiesContract(state.get('network'))
    token = getTokenContract(state.get('network'), to_checksum_address(state.get('token_address')))

    platform_fees = int(state.get('platform').get('fees_factor') * state.get('amount'))

    # Pay Platform Fees
    platform_fees_tx = token.functions.approve(
        to_checksum_address(state.get('platform').get('address')),
        platform_fees
    ).buildTransaction({
        'gasPrice': web3.toWei(state.get('gas_price'), 'gwei'),
        'gas': state.get('gas_limit'),
        'nonce': web3.eth.getTransactionCount(to_checksum_address(state.get('wallet').get('address'))),
    })

    platform_fees_tx_signed = web3.eth.account.signTransaction(platform_fees_tx, private_key=state.get('wallet').get('private_key'))

    # send transaction and wait for receipt
    print('Approving token usage to pay platform fees to gitcoin... ', end='', flush=True)
    platform_fees_tx_receipt = web3.eth.waitForTransactionReceipt(web3.eth.sendRawTransaction(platform_fees_tx_signed.rawTransaction))
    puts(colored.green(web3.toHex(platform_fees_tx_receipt.transactionHash)))

    tx = token.functions.approve(
        to_checksum_address(bountiesContract.address),
        state.get('amount')
    ).buildTransaction({
        'gasPrice': web3.toWei(state.get('gas_price'), 'gwei'),
        'gas': state.get('gas_limit'),
        'nonce': web3.eth.getTransactionCount(to_checksum_address(state.get('wallet').get('address'))),
    })

    signed = web3.eth.account.signTransaction(tx, private_key=state.get('wallet').get('private_key'))

    # send transaction and wait for receipt
    print('Approving token usage to fund bounty... ', end='', flush=True)
    receipt = web3.eth.waitForTransactionReceipt(web3.eth.sendRawTransaction(signed.rawTransaction))
    puts(colored.green(web3.toHex(receipt.transactionHash)))
