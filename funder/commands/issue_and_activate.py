# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import os
import json

from math import pow

from clint.textui import puts, colored
from eth_utils import to_checksum_address

from config.web3 import web3_client
from config.contracts import getTokenContract, getBountiesContract
from utils.wallet import Wallet
from utils.ipfs import saveToIPFS
from utils.token import getTokenInfo, approveTokenTransfer
from utils.token_list import name_to_token

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
        'gas': state.get('gas_limit'),
        'nonce': web3.eth.getTransactionCount(state.get('wallet').get('address'))
    })

    signed = web3.eth.account.signTransaction(tx, private_key=state.get('wallet').get('private_key'))

    old_id = bountiesContract.functions.getNumBounties().call()

    # send transaction and wait for receipt
    print('Funding bounty... ', end='', flush=True)
    receipt = web3.eth.waitForTransactionReceipt(web3.eth.sendRawTransaction(signed.rawTransaction))
    new_id = bountiesContract.functions.getNumBounties().call()
    puts(colored.green(web3.toHex(receipt.transactionHash)))

    return old_id < new_id, old_id

def canUserFundBounty(state):
    web3 = web3_client(state.get('network'))
    address = to_checksum_address(state.get('wallet').get('address'))

    # if the user is funding the bounty with a token, ensure they have enough tokens
    if(state.get('token_address') != '0x0000000000000000000000000000000000000000'):
        token = getTokenContract(state.get('network'), to_checksum_address(state.get('token_address')))
        token_balance = token.functions.balanceOf(address).call()

        if(token_balance < state.get('amount')):
            return False

    # need to account for gas limit regardless, only add amount if bounty is funded using ether

    eth_amount = state.get('amount') if state.get('token_address') == '0x0000000000000000000000000000000000000000' else state.get('gas_limit')
    eth_balance = web3.eth.getBalance(address)

    return eth_amount < eth_balance

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
    puts(colored.green(ipfsHash))

    # set address to valid checksum address for transaction
    state.get('wallet').update({ 'address' : to_checksum_address(state.get('wallet').get('address')) })

    # approve the token transfer if using EIP20
    if(state.get('token_address') != '0x0000000000000000000000000000000000000000'):
        approveTokenTransfer(state)

    # issue and activate bounty
    result, id = issueAndActivateBounty(state, ipfsHash)

    print(f'Bounty {id} funded successfully!') if result else print('Error funding bounty!')
