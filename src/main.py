# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import os
import json

sys.path.insert(0, os.path.abspath('..'))

from clint.textui import puts, colored, indent
from clint.arguments import Args

from web3 import Web3
from web3.middleware import geth_poa_middleware # used to connect to rinkeby

from utils import getBountyContract
from input import getUserInput
from ipfs import submitToIPFS

# contract = getBountyContract('mainnet')
# print(contract.functions.bounties(550).call())
#
# import ipfsapi
# ipfs = ipfsapi.connect('https://ipfs.infura.io', 5001)
# print(repr(ipfs.cat('QmSZV3GbG98pAegEq5newg9en4ioWmiCvefqjVbT79Kxkr')))
# exit(0)


# var expire_date = parseInt(expirationTimeDelta) + ((new Date().getTime() / 1000) | 0);
# var mock_expire_date = 9999999999; // 11/20/2286, https://github.com/Bounties-Network/StandardBounties/issues/25

def main():
    args = Args()

    with indent(4, quote=''):
        puts(colored.red('Grouped Arguments: ') + str(dict(args.grouped)))

    data = {}

    if( args.grouped.get('--json') ):
        # TODO validate file
        with open(args.grouped.get('--json')[0]) as f:
            data = json.load(f)
    else:
        data = getUserInput(args)

    #print(data)
    print(submitToIPFS(data))


# 1. post data to ipfs


# 2. approve token transfer (only if needed)
# 3. issue and activate bounty

if __name__ == '__main__':
    main()
