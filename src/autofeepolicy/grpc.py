from glob import glob
from .utils import config
from requests import request

class Grpc:

    def __init__(self, datadir: str, network: str, restlisten: str=None):
        if (datadir[-1] == '/'):
            self.datadir = datadir[:-1]
        else:
            self.datadir = datadir
        
        self.network = network
        self.tlscert = f'{self.datadir}/tls.cert'

        if restlisten:
            self.restlisten = restlisten
        else:
            self.config = config.load(f'{self.datadir}/lnd.conf')
            self.restlisten = self.config.get(
                'restlisten', '127.0.0.1:8080'
            )

        self.rpchost = f'https://{self.restlisten}/v1'
        self.macaroon = f'{self.datadir}/data/chain/bitcoin/{self.network}/admin.macaroon'
        if not glob(self.macaroon):
            self.macaroon = self.macaroon.replace('/data','')
        
        with open(self.macaroon, 'rb') as file_macaroon:
            self.macaroon = file_macaroon.read().hex()

    def call(self, method: str, path: str, **data: dict) -> dict:
        headers = {'Grpc-Metadata-macaroon': self.macaroon}
        push = request(
            method=method, url=f'{self.rpchost}/{path}', json=data, 
            headers=headers, verify=self.tlscert
        )
        assert push.status_code == 200, push.text
        yield push.json()

    def getinfo(self) -> dict:
        yield next(self.call('get', 'getinfo'))
    
    def listchannels(self) -> dict:
        yield next(self.call('get', 'channels'))['channels']
    
    def filterchannel(self, identify: str) -> dict:
        channel = list(filter(
            lambda channel: channel['chan_id'] == str(identify) or channel['remote_pubkey'] == str(identify), \
                next(self.listchannels())
        ))
        yield channel

    def getnodeinfo(self, pubkey: str) -> dict:
        yield next(self.call('get', f'graph/node/{pubkey}'))['node']
    
    def getchaninfo(self, chainid: str) -> dict:
        yield next(self.call('get', f'graph/edge/{chainid}'))