import json
from urllib.parse import urlparse

from click import BadParameter

from config.web3 import web3_client
from config.contracts import getBountiesContract, UnsupportedNetworkException
from utils.token_list import name_to_token

def network(ctx, param, value):
    try:
        getBountiesContract(value)
    except UnsupportedNetworkException:
        raise BadParameter('unsupported network')
    return value

def secret(ctx, param, value):
    try:
        with open(value) as f:
            data = json.load(f)

        if(not data.get('mnemonic')):
            raise BadParameter('mnemonic not found in json')

    except FileNotFoundError:
        raise BadParameter(f'{value} not found')
    except json.decoder.JSONDecodeError:
        raise BadParameter(f'{value} not valid json')

    return value

def token(ctx, param, value):
    if(not name_to_token(value)):
        raise BadParameter(f'{value} not supported by symbol, please use only --token-address')

    return value

# TODO
# def token_address(ctx, param, value)

def url(ctx, param, value):
    url = urlparse(value)

    if(url.netloc.lower() != 'github.com'):
        raise BadParameter('url must be GitHub link')

    return value

def amount(ctx, param, value):
    if(0 >= value):
        raise BadParameter('bounty amount cannot be negative')

    return value
