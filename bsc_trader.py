from bsc_transfer import BscTransfer
from pancakeswap_config import pancakeswap_router_abi, pancakeswap_router_address, wbnb_address, \
    transaction_timeout_seconds, swap_gas_limit


class BscTrader(BscTransfer):
    def __init__(self):
        super().__init__()
        self.pancakeswap_router = self.web3.eth.contract(
            address=self.to_checksum_address(pancakeswap_router_address),
            abi=pancakeswap_router_abi
        )
        self.refresh_balance()

    def refresh_balance(self):
        self.wei_bnb_balance = self.web3.eth.get_balance(self.source_checksum_address)
        self.wei_token_balance = self.contract.functions.balanceOf(self.source_checksum_address).call()
        self.bnb_balance = self.web3.from_wei(self.wei_bnb_balance, 'ether')
        self.token_balance = self.web3.from_wei(self.wei_token_balance, 'ether')
        print("-" * 30)
        print(f"BNB 余额: {self.bnb_balance:,.5f} BNB")
        print(f"NIAO 余额: {self.token_balance:,.2f} NIAO")
        print("-" * 30)
        if self.trans_count > 0:
            print(f"已完成交易次数: {self.trans_count}")

    def check_balance(self, address, amount_wei, token_type="BNB"):
        if token_type == "BNB":
            balance = self.web3.eth.get_balance(address)
        else:
            balance = self.contract.functions.balanceOf(address).call()

        if balance < amount_wei:
            raise ValueError(f"{token_type} 余额不足")

    def prepare_transaction(self, from_address, amount_in, amount_out_min, swap_function, path):
        nonce = self.get_next_nonce()
        gas_price = self.web3.eth.gas_price
        deadline = self.web3.eth.get_block('latest')['timestamp'] + transaction_timeout_seconds

        return swap_function(
            amount_in,
            amount_out_min,
            path,
            from_address,
            deadline
        ).build_transaction({
            'from': from_address,
            'gas': swap_gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': self.web3.eth.chain_id,
        })

    def execute_transaction(self, transaction):
        signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key=self._private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    def buy(self, amount_tokens: float):
        amount_out = self.web3.to_wei(amount_tokens, 'ether')

        path = [wbnb_address, self.contract.address]
        swap_function = self.pancakeswap_router.functions.swapETHForExactTokens

        # 获取购买所需的 BNB 数量
        amounts_in = self.pancakeswap_router.functions.getAmountsIn(amount_out, path).call()
        amount_in = amounts_in[0]

        # 设置滑点，例如允许实际支付的 BNB 比估算多 5%
        max_amount_in = int(amount_in * 1.05)

        # 检查 BNB 余额
        self.check_balance(self.source_checksum_address, max_amount_in, "BNB")

        deadline = self.web3.eth.get_block('latest')['timestamp'] + transaction_timeout_seconds

        swap_tx = swap_function(
            amount_out,  # 要购买的确切代币数量
            path,
            self.source_checksum_address,
            deadline
        ).build_transaction({
            'from': self.source_checksum_address,
            'gas': swap_gas_limit,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': self.get_next_nonce(),
            'chainId': self.web3.eth.chain_id,
            'value': max_amount_in  # 为买入操作添加 value，允许滑点
        })

        tx_receipt = self.execute_transaction(swap_tx)

        if tx_receipt['status'] == 1:
            self.trans_count += 1
            cost_value = f"{self.web3.from_wei(max_amount_in, 'ether'):,.8f}"
            print(f"买入交易成功。购买了 {amount_tokens} 代币，最多花费 {cost_value} BNB。")
        else:
            print(f"买入交易失败。")
        self.refresh_balance()

    def sell(self, amount_tokens: float):
        amount_in = self.web3.to_wei(amount_tokens, 'ether')
        self.check_balance(self.source_checksum_address, amount_in, "Token")

        # 授权 PancakeSwap 路由器使用代币
        approve_tx = self.contract.functions.approve(
            self.pancakeswap_router.address,
            amount_in
        ).build_transaction({
            'from': self.source_checksum_address,
            'gas': swap_gas_limit,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': self.get_next_nonce(),
            'chainId': self.web3.eth.chain_id,
        })

        approve_receipt = self.execute_transaction(approve_tx)
        if approve_receipt['status'] != 1:
            print("授权失败")
            return

        path = [self.contract.address, wbnb_address]
        swap_function = self.pancakeswap_router.functions.swapExactTokensForETH

        # 获取预期的 BNB 输出量
        amounts_out = self.pancakeswap_router.functions.getAmountsOut(amount_in, path).call()
        amount_out_min = int(amounts_out[1] * 0.95)  # 设置滑点为 5%

        swap_tx = self.prepare_transaction(self.source_checksum_address, amount_in, amount_out_min, swap_function, path)

        tx_receipt = self.execute_transaction(swap_tx)

        if tx_receipt['status'] == 1:
            self.trans_count += 1
            delta_value = f"{self.web3.from_wei(amount_out_min, 'ether'):,.8f}"
            print(f"卖出交易成功。卖出 {amount_tokens} 代币，获得至少 {delta_value} BNB。")
        else:
            print(f"卖出交易失败。")
        self.refresh_balance()