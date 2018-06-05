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

APPROVE_GAS = 70000
BOUNTY_GAS = 318730

def getTokenInfo(state):
    # get token address and decimal places
    token = name_to_token(state.get('token'))

    # user wants to use custom token if address != 0x0
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

    return {
        'token': token.get('name'),
        'token_address': token.get('addr'),
        'token_decimals': int(token.get('decimals')),
        'amount': int(state.get('amount') * pow( 10, int(token.get('decimals'))) )
    }

def approveTokenTransfer(state):
    web3 = web3_client(state.get('network'))
    bountiesContract = getBountiesContract(state.get('network'))
    t = getTokenContract(state.get('network'), to_checksum_address(state.get('token_address')))

    # TODO verify there are enough tokens for bounty
    tx = t.functions.approve(
        to_checksum_address(bountiesContract.address),
        state.get('amount')
    ).buildTransaction({
        'gasPrice': web3.toWei(state.get('gas_price'), 'gwei'),
        'gas': APPROVE_GAS,
        'nonce': web3.eth.getTransactionCount(to_checksum_address(state.get('wallet').get('address'))),
    })

    signed = web3.eth.account.signTransaction(tx, private_key=state.get('wallet').get('private_key'))

    # send transaction and wait for receipt
    print('Approving token usage... ', end='', flush=True)
    receipt = web3.eth.waitForTransactionReceipt(web3.eth.sendRawTransaction(signed.rawTransaction))
    puts(colored.green('done.'))

def issueAndActivateBounty(state, ipfsHash):
    web3 = web3_client(state.get('network'))
    bountiesContract = getBountiesContract(state.get('network'))

    # build transaction
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
        'gasPrice': web3.toWei(state.get('gas_price'), 'gwei'),
        'gas': BOUNTY_GAS,
        'nonce': web3.eth.getTransactionCount(state.get('wallet').get('address'))
    })

    signed = web3.eth.account.signTransaction(tx, private_key=state.get('wallet').get('private_key'))

    old_id = bountiesContract.functions.getNumBounties().call()

    # send transaction and wait for receipt
    print('Funding bounty... ', end='', flush=True)
    receipt = web3.eth.waitForTransactionReceipt(web3.eth.sendRawTransaction(signed.rawTransaction))
    new_id = bountiesContract.functions.getNumBounties().call()
    puts(colored.green('done.'))

    return old_id < new_id, old_id

def canUserFundBounty(state):
    web3 = web3_client(state.get('network'))

    if(state.get('token_address') != '0x0000000000000000000000000000000000000000'):
        t = getTokenContract(state.get('network'), to_checksum_address(state.get('token_address')))
        token_balance = t.functions.balanceOf(to_checksum_address(state.get('wallet').get('address'))).call()

        if(token_balance < state.get('amount')):
            return False

    eth_amount = state.get('amount') + BOUNTY_GAS if state.get('token_address') == '0x0000000000000000000000000000000000000000' else BOUNTY_GAS
    eth_balance = web3.eth.getBalance(to_checksum_address(state.get('wallet').get('address')))

    return eth_balance < eth_amount

def handler(state):
    # update state with token info
    state.update(getTokenInfo(state))

    # make sure user has enough funds for bounty
    if(not canUserFundBounty(state)):
        print('Not enough funds to issue bounty!')
        exit(1)

    # post data to ipfs
    print('Saving data to IPFS... ', end='', flush=True)
    ipfsHash = saveToIPFS(state)
    puts(colored.green('done.'))

    # set address to valid checksum address for transaction
    state.get('wallet').update({ 'address' : to_checksum_address(state.get('wallet').get('address')) })

    # approve the token transfer if using EIP20
    if(state.get('token_address') != '0x0000000000000000000000000000000000000000'):
        approveTokenTransfer(state)

    # issue and activate bounty
    result, id = issueAndActivateBounty(state, ipfsHash)

    print(f'Bounty {id} funded successfully!') if result else print('Error funding bounty!')
