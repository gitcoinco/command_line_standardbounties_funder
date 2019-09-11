import json
from web3 import HTTPProvider, Web3
from web3.middleware import geth_poa_middleware # used to connect to rinkeby


class UnsupportedNetworkException(Exception):
    pass

def web3_client(network):
    infura_project_id = '784a07739746401087167693317c5864'
    if network in ['mainnet', 'rinkeby', 'ropsten']:
        web3 = Web3(HTTPProvider(f'https://{network}.infura.io/v3/{infura_project_id}'))

        if network == 'rinkeby':
            web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        return web3

    raise UnsupportedNetworkException(network)
