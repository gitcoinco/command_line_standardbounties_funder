# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import os
import json

from math import pow

from click import confirm
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

    platform_fees = int(state.get('platform').get('fees_factor') * state.get('amount'))
    if state.get('token_address') == '0x0000000000000000000000000000000000000000':
        # build transaction to pay the platform fees
        platform_fees_tx = {
            'from': state.get('wallet').get('address'),
            'to': state.get('platform').get('address'),
            'gas': state.get('gas_limit'),
            'gasPrice': web3.toWei(state.get('gas_price'), 'gwei'),
            'value': platform_fees,
            'nonce': web3.eth.getTransactionCount(state.get('wallet').get('address'))
        }

        signed_platform_fees_tx = web3.eth.account.signTransaction(platform_fees_tx, private_key=state.get('wallet').get('private_key'))

        # send platform fees transaction and wait for receipt
        print('Sending platform fees to gitcoin... ', end='', flush=True)
        platform_fees_receipt = web3.eth.waitForTransactionReceipt(web3.eth.sendRawTransaction(signed_platform_fees_tx.rawTransaction))
        puts(colored.green(web3.toHex(platform_fees_receipt.transactionHash)))

    else:
        tokenContract = getTokenContract(state.get('network'), state.get('token_address'))
        platform_fees_tx = tokenContract.transfer(
            to_checksum_address(state.get('platform').get('address')),
            platform_fees
        ).buildTransaction({
            'from': state.get('wallet').get('address'),
            'gasPrice': web3.toWei(state.get('gas_price'), 'gwei'),
            'gas': state.get('gas_limit'),
            'nonce': web3.eth.getTransactionCount(to_checksum_address(state.get('wallet').get('address')))
        })
        signed_platform_fees_tx = web3.eth.account.signTransaction(platform_fees_tx, private_key=state.get('wallet').get('private_key'))

        # send platform fees transaction and wait for receipt
        print('Sending platform fees to gitcoin... ', end='', flush=True)
        platform_fees_receipt = web3.eth.waitForTransactionReceipt(web3.eth.sendRawTransaction(signed_platform_fees_tx.rawTransaction))
        puts(colored.green(web3.toHex(platform_fees_receipt.transactionHash)))

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

def canUserFundBounty(state, ether, tokens=0):
    # check if user has enough ether
    # need to account for gas limit regardless, only add amount if bounty is funded using ether
    # need to do two transactions, one to the bountiesNetwork and other as platform fees to gitcoin
    amount = 2 * state.get('gas_limit')

    bounty_amount_with_platform_fees = state.get('amount') * ( 1.0 + state.get('platform').get('fees_factor') )

    if state.get('token_address') == '0x0000000000000000000000000000000000000000':
        amount += bounty_amount_with_platform_fees

    # check if user has enough tokens
    elif(tokens < bounty_amount_with_platform_fees):
        return False

    return amount < ether

def tokenBalance(state):
    web3 = web3_client(state.get('network'))
    address = to_checksum_address(state.get('wallet').get('address'))
    token_balance = 0

    # if the user is funding the bounty with a token, ensure they have enough tokens
    if(state.get('token_address') != '0x0000000000000000000000000000000000000000'):
        token = getTokenContract(state.get('network'), to_checksum_address(state.get('token_address')))
        token_balance = token.functions.balanceOf(address).call()

    return token_balance

def etherBalance(state):
    web3 = web3_client(state.get('network'))
    address = to_checksum_address(state.get('wallet').get('address'))
    return web3.eth.getBalance(address)


def handler(state):
    print(f'Funding from {state.get("wallet").get("address")}')

    # update state with token info
    state.update(getTokenInfo(state))

    ether_balance = etherBalance(state)
    token_balance = tokenBalance(state)

    if(state.get('token') != 'ETH'):
        print(f'Token balance: {token_balance * pow(10, -1 * state.get("token_decimals"))}')

    print(f'Ether balance: {ether_balance * pow(10, -18)}')

    if(not state.get('confirmed')):
        if (not confirm(('An additional {}% platform additional platform fees will be charged, Do you want to continue?')
                .format(state.get('platform').get('fees_factor') * 100))):
            print('Aborted!\n')
            exit(1)

    # make sure user has enough funds for bounty
    if(not canUserFundBounty(state, ether_balance, token_balance)):
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
