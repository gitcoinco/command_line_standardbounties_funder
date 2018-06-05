from time import time
import ipfsapi

def ipfs_client():
    return ipfsapi.connect('https://ipfs.infura.io', 5001)

def saveToIPFS(data):
    payload = buildPayload(data)
    ipfs = ipfs_client()

    # adds json-serializable Python dict as a json file to IPFS
    # https://python-ipfs-api.readthedocs.io/en/stable/api_ref.html#ipfsapi.Client.add_json
    return ipfs.add_json(payload)

def buildPayload(data):
    privacy_preferences = {
        'show_email_publicly': data.get('show_email'),
        'show_name_publicly': data.get('show_name')
    }

    metadata = {
        'issueTitle': data.get('title'),
        'issueDescription': data.get('description'),
        'issueKeywords': data.get('keywords'),
        'githubUsername': data.get('github'),
        'notificationEmail': data.get('notification_email'),
        'fullName': data.get('full_name'),
        'experienceLevel': data.get('experience'),
        'projectLength': data.get('length'),
        'bountyType': data.get('type'),
        'tokenName': data.get('token')
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
                'address': data.get('wallet').get('address')
            },

            'privacy_preferences': privacy_preferences,
            'funders': [],
            'categories': metadata.get('issueKeywords'),
            'created': int(time()),
            'webReferenceURL': data.get('url'),

            # optional fields
            'metadata': metadata,
            'tokenName': data.get('token'),
            'tokenAddress': data.get('token_address'),
            'expire_date': 9999999999, # 11/20/2286, https://github.com/Bounties-Network/StandardBounties/issues/25
            },

            'meta': {
                'platform': 'gitcoin',
                'schemaVersion': '0.1',
                'schemaName': 'gitcoinBounty'
            }
        }

    return payload
