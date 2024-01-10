import web3
from eth_account.messages import encode_defunct
from web3.middleware import geth_poa_middleware

from carv import Carv

Web3 = web3.Web3

opbnb_rpc = ''
opbnb_w3 = Web3(Web3.HTTPProvider(opbnb_rpc))
opbnb_w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # Inject POA middleware

abi = (
    '[{"stateMutability": "nonpayable","type": "function","inputs": [{"name": "mintData","internalType": "struct '
    'Soul.MintData","type": "tuple","components": [{"name": "account","internalType": "address","type": "address"}, '
    '{"name": "amount","internalType": "uint256","type": "uint256"}, {"name": "ymd","internalType": "uint256",'
    '"type": "uint256"}]}, {"name": "signature","internalType": "bytes","type": "bytes"}],"name": "mintSoul",'
    '"outputs": []}]')


def opbnb_transaction(private_key, value, to, address, priority_fee, mint_data, signature):
    from_address = opbnb_w3.to_checksum_address(address)
    to_address = opbnb_w3.to_checksum_address(to)

    contract = opbnb_w3.eth.contract(address=to_address, abi=abi)
    mintData = (opbnb_w3.to_checksum_address(mint_data["account"]), mint_data["amount"], mint_data["ymd"])
    functions = contract.functions.mintSoul(mintData=mintData, signature=signature)

    value = opbnb_w3.to_wei(value, 'ether')

    base_fee = opbnb_w3.eth.get_block('latest')['baseFeePerGas']
    max_priority_fee_per_gas = opbnb_w3.to_wei(priority_fee, 'gwei')  # Tip for the miner, adjust as needed
    max_fee_per_gas = base_fee + max_priority_fee_per_gas

    gas_estimate = functions.estimate_gas({
        'value': value,
        'from': from_address,
    })

    tx = functions.build_transaction(transaction={
        'type': '0x2',  # Indicates an EIP-1559 transaction
        'chainId': opbnb_w3.eth.chain_id,
        'nonce': opbnb_w3.eth.get_transaction_count(from_address),
        'maxPriorityFeePerGas': max_priority_fee_per_gas,
        'maxFeePerGas': max_fee_per_gas,
        'gas': gas_estimate,
        'value': value
    })

    signed_tx = opbnb_w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = opbnb_w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = opbnb_w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt.transactionHash.hex()


if __name__ == '__main__':
    # 私钥
    private_key = ''
    # 代理
    proxies=None

    account = web3.Account.from_key(private_key)
    print(f'address: {account.address}')

    carv = ''

    login_flag = True
    while login_flag:
        try:
            carv = Carv(proxies=proxies)

            get_utc_res = carv.get_utc()

            # 钱包签名
            message = (f'Hello! Please sign this message to confirm your ownership of the address. This action '
                       f'will not cost any gas fee. Here is a unique text: {int(get_utc_res["unixtime"]) * 1000}')
            sign = opbnb_w3.eth.account.sign_message(signable_message=encode_defunct(text=message),
                                                     private_key=private_key)
            # 获取登录信息
            carv.login(address=account.address, signature=sign.signature.hex(), message=message)
            login_flag = False
        except Exception as e:
            print(f'login异常: {e}')

    ronin_check_in_flag = True
    while ronin_check_in_flag:
        try:
            # Ronin签到
            ronin_chain_id = '2020'
            ronin_status = carv.check_carv_status(ronin_chain_id)['data']['status']
            if ronin_status == 'not_started':
                ronin_check_in_res = carv.check_in(ronin_chain_id)
                print(f'Ronin签到: {ronin_check_in_res}')
            else:
                print(f'ronin签到状态: {ronin_status}')
            ronin_check_in_flag = False
        except Exception as e:
            print(f'Ronin签到异常: {e}')

    opbnb_check_in_flag = True
    while opbnb_check_in_flag:
        try:
            # opBnb签到
            opbnb_chain_id = opbnb_w3.eth.chain_id
            opbnb_status = carv.check_carv_status(opbnb_chain_id)['data']['status']
            if carv.check_carv_status(opbnb_chain_id)['data']['status'] == 'not_started':
                opbnb_check_in_res = carv.check_in(opbnb_chain_id)
                print(f'opBNB签到参数获取: {opbnb_check_in_res}')
                data = opbnb_check_in_res['data']
                priority_fee = 0.00001
                tx = opbnb_transaction(private_key=private_key, value=0, to=data['contract'],
                                       address=account.address,
                                       priority_fee=priority_fee, mint_data=data['permit'],
                                       signature=data['signature'])
                print(f'opBNB签到tx: {tx}')
            else:
                print(f'opBNB签到状态: {opbnb_status}')
            opbnb_check_in_flag = False
        except Exception as e:
            print(f'Ronin签到异常: {e}')

    data_rewards_flag = True
    while data_rewards_flag:
        try:
            data_rewards_list = carv.data_rewards_list()['data']['data_rewards']
            if data_rewards_list is not None and len(data_rewards_list) > 0:
                print(f'获取数据奖励')
                for data_rewards in data_rewards_list:
                    print(data_rewards)
                    data_rewards_claim = carv.data_rewards_claim(data_rewards['id'])
                    print(data_rewards_claim)
            data_rewards_flag = False
        except Exception as e:
            print(f'数据奖励签到异常: {e}')
    print('---------------------------------------------------------')
