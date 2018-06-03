from time import time
from utils import getIPFS

def saveToIPFS(data):
    payload = buildPayload(data)
    ipfs = getIPFS()

    # adds json-serializable Python dict as a json file to IPFS
    # https://python-ipfs-api.readthedocs.io/en/stable/api_ref.html#ipfsapi.Client.add_json
    return ipfs.add_json(payload)

def buildPayload(data):
    privacy_preferences = {
        'show_email_publicly': data.get('showEmailPublicly'),
        'show_name_publicly': data.get('showNamePublicly')
    }

    metadata = {
        'issueTitle': data.get('title'),
        'issueDescription': data.get('description'),
        'issueKeywords': data.get('keywords'),
        'githubUsername': data.get('githubUsername'),
        'notificationEmail': data.get('notificationEmail'),
        'fullName': data.get('fullName'),
        'experienceLevel': data.get('experienceLevel'),
        'projectLength': data.get('projectLength'),
        'bountyType': data.get('bountyType'),
        'tokenName': data.get('tokenName')
    }

    payload = {
        'payload': {
            'title': metadata.get('issueTitle'),
            'description': metadata.get('issueDescription'),
            'sourceFileName': '',
            'sourceFileHash': '',
            'sourceDirectoryHash': '',
            'issuer': {
                'name': metadata.get('fullName'),
                'email': metadata.get('notificationEmail'),
                'githubUsername': metadata.get('githubUsername'),
                'address': data.get('ethereumAddress')
            },

            'privacy_preferences': privacy_preferences,
            'funders': [],
            'categories': metadata.get('issueKeywords'),
            'created': int(time()),
            'webReferenceURL': data.get('issueURL'),

            # optional fields
            'metadata': metadata,
            'tokenName': data.get('tokenName'),
            'tokenAddress': data.get('tokenAddress'),
            'expire_date': data.get('expireDate')
            },

            'meta': {
                'platform': 'gitcoin',
                'schemaVersion': '0.1',
                'schemaName': 'gitcoinBounty'
            }
        }

    return payload
