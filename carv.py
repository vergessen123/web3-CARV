import requests
from fake_useragent import UserAgent
import json
import base64

headers = {
    'Origin': 'https://protocol.carv.io',
    'Referer': 'https://protocol.carv.io/',
    'Content-Type': 'application/json',
}


class Carv:
    def __init__(self, proxies=None):
        self.proxies = proxies

        ua = UserAgent()
        headers['User-Agent'] = ua.chrome

    def get_utc(self):
        url = 'https://worldtimeapi.org/api/timezone/etc/UTC'
        res = requests.get(url=url, headers=headers, proxies=self.proxies)
        return res.json()

    def login(self, address, signature, message):
        url = 'https://interface.carv.io/protocol/login'
        data = {
            "wallet_addr": address,
            "text": message,
            "signature": signature
        }
        res = requests.post(url=url, headers=headers, data=json.dumps(data), proxies=self.proxies)

        login_res = res.json()
        token = f"eoa:{login_res['data']['token']}"
        headers['Authorization'] = 'bearer ' + base64.b64encode(token.encode('utf-8')).decode('utf-8')

    def check_carv_status(self, chain_id):
        url = f'https://interface.carv.io/airdrop/check_carv_status?chain_id={chain_id}'
        res = requests.get(url=url, headers=headers, proxies=self.proxies)
        return res.json()

    def check_in(self, chain_id):
        url = f'https://interface.carv.io/airdrop/mint/carv_soul'
        data = {
            "chain_id": chain_id
        }
        res = requests.post(url=url, headers=headers, data=json.dumps(data), proxies=self.proxies)
        return res.json()

    def data_rewards_list(self):
        url = f'https://interface.carv.io/airdrop/data_rewards/list'
        res = requests.get(url=url, headers=headers)
        return res.json()

    def data_rewards_claim(self, id):
        url = f'https://interface.carv.io/airdrop/data_rewards/claim'
        data = {
            "id": id
        }
        res = requests.post(url=url, headers=headers, data=json.dumps(data), proxies=self.proxies)
        return res.json()

    def get_balance(self):
        url = 'https://interface.carv.io/airdrop/soul/balance'
        res = requests.get(url=url, headers=headers)
        return res.json()
