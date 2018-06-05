# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import os
import json

from math import pow

from clint.textui import puts, colored
from eth_utils import to_checksum_address

from utils.wallet import Wallet
from utils.web3 import web3_client
from utils.contracts import getTokenContract, getBountiesContract
from utils.token_list import name_to_token
from utils.ipfs import saveToIPFS

def issueAndActivateBounty(state):
    web3 = web3_client(state.get('network'))
    bountiesContract = getBountiesContract(state.get('network'))

    # get token address and decimal places
    token = name_to_token(state.get('token'))

    # user wants to use custom token
    if(state.get('token_address') != '0x0000000000000000000000000000000000000000'):
        t = getTokenContract(state.get('network'), to_checksum_address(state.get('token_address')))

        print('Getting token info... ', end='', flush=True)
        token.update({
            #'name' : t.functions.name().call()),
            'addr': state.get('token_address'),
            'name': t.functions.symbol().call(),
            'decimals': t.functions.decimals().call()
        })
        puts(colored.green('done.'))

    # no token name was used
    if(not token):
        print(f'Error {data.get("tokenName")} is not supported.')
        exit(1)

    # update state with new token info
    state.update({
        'token': token.get('name'),
        'token_address': token.get('addr'),
        'token_decimals': int(token.get('decimals')),
        'amount': int(state.get('amount') * pow( 10, int(token.get('decimals'))) )
    })

    # post data to ipfs
    print('Saving data to IPFS... ', end='', flush=True)
    ipfsHash = saveToIPFS(state)
    puts(colored.green('done.'))

    # set address to valid checksum address for transaction
    state.get('wallet').update({ 'address' : to_checksum_address(state.get('wallet').get('address')) })

    if(state.get('token_address') != '0x0000000000000000000000000000000000000000'):
        # TODO verify there are enough tokens for bounty
        tx = t.functions.approve(
            to_checksum_address(bountiesContract.address),
            state.get('amount')
        ).buildTransaction({
            'gasPrice': web3.toWei('5', 'gwei'),
            'gas': 70000,
            'nonce': web3.eth.getTransactionCount(to_checksum_address(state.get('wallet').get('address'))),
        })

        signed = web3.eth.account.signTransaction(tx, private_key=state.get('wallet').get('private_key'))

        # send transaction and wait for receipt
        print('Approving token usage... ', end='', flush=True)
        receipt = web3.eth.waitForTransactionReceipt(web3.eth.sendRawTransaction(signed.rawTransaction))
        puts(colored.green('done.'))



    tx = bountiesContract.functions.issueAndActivateBounty(
        state.get('wallet').get('address'),
        9999999999, # 11/20/2286, https://github.com/Bounties-Network/StandardBounties/issues/25
        ipfsHash,
        state.get('amount'),
        '0x0000000000000000000000000000000000000000',
        state.get('token_address') != '0x0000000000000000000000000000000000000000',
        to_checksum_address(state.get('token_address')),
        state.get('amount')
    ).buildTransaction({
        'from': state.get('wallet').get('address'),
        'value': state.get('amount') if state.get('token_address') == '0x0000000000000000000000000000000000000000' else 0,
        'gasPrice': web3.toWei('5', 'gwei'),
        'gas': 318730,
        'nonce': web3.eth.getTransactionCount(state.get('wallet').get('address'))
    })

    signed = web3.eth.account.signTransaction(tx, private_key=state.get('wallet').get('private_key'))

    old_id = bountiesContract.functions.getNumBounties().call()

    # send transaction and wait for receipt
    print('Funding bounty... ', end='', flush=True)
    receipt = web3.eth.waitForTransactionReceipt(web3.eth.sendRawTransaction(signed.rawTransaction))
    new_id = bountiesContract.functions.getNumBounties().call()
    puts(colored.green('done.'))

    if(old_id < new_id):
        print('')
        print(f'Bounty {old_id} funded successfully!')
    else:
        print('Error funding bounty!')
