from web3 import Web3
from config import abi
from private import private_key, contract_address

nonce = None


class BscTransfer:
    def __init__(self):
        self._private_key = private_key
        self.bsc = "https://bsc-dataseed.binance.org/"
        self.web3 = Web3(Web3.HTTPProvider(self.bsc))
        self.trans_count = 0
        if not self.web3.is_connected():
            raise Exception("Failed to connect to BSC network")
        print("Connected to BSC network")

        self.contract = self.web3.eth.contract(address=self.to_checksum_address(contract_address), abi=abi)

        total_supply = self.contract.functions.totalSupply().call()
        name = self.contract.functions.name().call()
        symbol = self.contract.functions.symbol().call()

        print(f"Token Name: {name}")
        print(f"Token Symbol: {symbol}")
        print(f"Total Supply: {self.web3.from_wei(total_supply, 'ether')} {symbol}")

    def to_checksum_address(self, address):
        return self.web3.to_checksum_address(address)

    def transfer(self, from_address: str, receive_address: str, amount: float):

        if not self.web3.is_address(from_address) or not self.web3.is_address(receive_address):
            raise ValueError("Invalid address provided")
        source_address = self.to_checksum_address(from_address)
        destination_address = self.to_checksum_address(receive_address)
        balance = self.contract.functions.balanceOf(source_address).call()
        print(f"Balance of sender: {self.web3.from_wei(balance, 'ether')} tokens")

        if balance < amount:
            raise ValueError("Insufficient balance")

        amount_wei = self.web3.to_wei(amount, 'ether')

        # 在以太坊和类似的区块链网络中，每个地址都有一个 nonce 值，它代表该地址发送的交易数量。每次发送新交易时，nonce 值都应该比上一次交易的 nonce 值高 1
        global nonce
        if nonce is None:
            nonce = self.web3.eth.get_transaction_count(source_address)
        else:
            nonce += 1

        gas_price = self.web3.eth.gas_price
        gas_limit = 100000

        token_tx = self.contract.functions.transfer(destination_address, amount_wei).build_transaction({
            'chainId': 56,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
        })

        signed_txn = self.web3.eth.account.sign_transaction(token_tx, private_key=self._private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # Wait for transaction receipt
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        if tx_receipt['status'] == 1:
            self.trans_count += 1
            print(f"{self.trans_count} transferred {amount} tokens to {receive_address}")
        else:
            print(f"Transaction failed. {amount} tokens to {receive_address}")

