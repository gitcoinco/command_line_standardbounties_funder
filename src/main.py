# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import os
import json

sys.path.insert(0, os.path.abspath('..'))

from math import pow

from clint.textui import puts, colored, indent
from clint.arguments import Args

from utils import getWeb3, getBountiesContract, getToken, getWallet, to_checksum_address
from utils.tokens import name_to_token
from utils.ipfs import saveToIPFS

from input import getUserInput

def main(args):
    network = args.grouped.get('--network')
    network = network[0] if network else 'rinkeby'

    web3 = getWeb3(network)
    wallet = getWallet(0)
    bountiesContract = getBountiesContract(network)
    data = { 'ethereumAddress' : to_checksum_address(wallet.get('address')) }

    # if a json was provided, use that create the bounty, otherwise go to interactive mode
    if( args.grouped.get('--json') ):
        # TODO validate json exists
        with open(args.grouped.get('--json')[0]) as f:
            data.update(json.load(f))
    else:
        data.update(getUserInput(args))


    # get token address and decimal places
    token = name_to_token(data.get('tokenName'))

    if(not token):
        print(f'Error {data.get("tokenName")} is not supported.')
        exit(1)

    data.update({
        'tokenAddress': token.get('addr'),
        'tokenDecimals': int(token.get('decimals')),
        'amount': int(data.get('amount') * pow( 10, int(token.get('decimals'))) )
    })

    # 1. post data to ipfs
    print('Saving data to IPFS... ', end='', flush=True)
    ipfsHash = saveToIPFS(data)
    puts(colored.green('done.'))


    # 2. approve token transfer (only if needed)
    if(data.get('tokenAddress') != '0x0000000000000000000000000000000000000000'):
        token = getToken(data.get('tokenAddress'))

        # TODO verify there are enough tokens for bounty
        tx = token.functions.approve(
            bountiesContract.address,
            data.get(amount),
        ).buildTransaction({
            'gasPrice': web3.toWei('5', 'gwei'),
            'gas': 70000,
            'nonce': web3.eth.getTransactionCount(data.get('ethereumAddress')),
        })


    # 3. issue and activate bounty
    # TODO verify there is enough ether to cover gas + bounty
    tx = bountiesContract.functions.issueAndActivateBounty(
        data.get('ethereumAddress'),
        9999999999, # 11/20/2286, https://github.com/Bounties-Network/StandardBounties/issues/25
        ipfsHash,
        data.get('amount'),
        '0x0000000000000000000000000000000000000000',
        data.get('tokenAddress') != '0x0000000000000000000000000000000000000000',
        data.get('tokenAddress'),
        data.get('amount')
    ).buildTransaction({
        'from': data.get('ethereumAddress'),
        'value': data.get('amount'),
        'gasPrice': web3.toWei('5', 'gwei'),
        'gas': 318730,
        'nonce': web3.eth.getTransactionCount(data.get('ethereumAddress'))
    })

    signed = web3.eth.account.signTransaction(tx, private_key=wallet.get('private_key'))

    # send transaction and wait for receipt
    print('Funding bounty... ', end='', flush=True)
    old_id = bountiesContract.functions.getNumBounties().call()
    receipt = web3.eth.waitForTransactionReceipt(web3.eth.sendRawTransaction(signed.rawTransaction))
    new_id = bountiesContract.functions.getNumBounties().call()
    puts(colored.green('done.'))

    if(old_id < new_id):
        print('')
        print(f'Bounty {old_id} funded successfully!')
    else:
        print('Error funding bounty!')

if __name__ == '__main__':
    args = Args()

    # with indent(4, quote=''):
    #     puts(colored.red('Grouped Arguments: ') + str(dict(args.grouped)))

    main(args)
