from web3 import Web3
from config import abi, gas_limit, chain_id
from private import private_key, contract_address


class BscTransfer:
    def __init__(self):
        self._nonce = None
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

    def get_next_nonce(self, from_address: str) -> int:
        if self._nonce is None:
            self._nonce = self.web3.eth.get_transaction_count(self.to_checksum_address(from_address))
        else:
            self._nonce += 1
        return self._nonce

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

        nonce = self.get_next_nonce(from_address)
        gas_price = self.web3.eth.gas_price

        token_tx = self.contract.functions.transfer(destination_address, amount_wei).build_transaction({
            'chainId': chain_id,
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

