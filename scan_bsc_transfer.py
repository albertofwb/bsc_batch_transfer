from typing import Dict

import requests
from web3 import Web3
from decimal import Decimal

from private import bsc_api_key


def scan_bsc_assets(wallet_address: str, bscscan_api_key: str) -> Dict[str, Decimal]:
    bsc_web3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))
    bsc_balance = bsc_web3.eth.get_balance(wallet_address)
    bsc_assets = {"BNB": Decimal(bsc_web3.from_wei(bsc_balance, "ether"))}

    bscscan_url = f"https://api.bscscan.com/api?module=account&action=tokentx&address={wallet_address}&startblock=0&endblock=999999999&sort=asc&apikey={bscscan_api_key}"
    response = requests.get(bscscan_url)

    if response.status_code == 200:
        result = response.json()
        token_transfers = result["result"]

        token_balances = {}

        for transfer in token_transfers:
            token_symbol = transfer["tokenSymbol"]
            token_decimals = int(transfer["tokenDecimal"])
            token_value = Decimal(transfer["value"]) / Decimal(10 ** token_decimals)

            if transfer["to"].lower() == wallet_address.lower():
                # Incoming transfer
                if token_symbol in token_balances:
                    token_balances[token_symbol] += token_value
                else:
                    token_balances[token_symbol] = token_value
            else:
                # Outgoing transfer
                if token_symbol in token_balances:
                    token_balances[token_symbol] -= token_value
                else:
                    token_balances[token_symbol] = -token_value

        for token_symbol, balance in token_balances.items():
            if balance > 0:
                bsc_assets[token_symbol] = balance
    return bsc_assets


NIAO_TOKEN_SYMBOL = "NIAO"


def has_interact_with_niao(wallet_address: str, bscscan_api_key: str) -> bool:
    bscscan_url = f"https://api.bscscan.com/api?module=account&action=tokentx&address={wallet_address}&startblock=0&endblock=999999999&sort=asc&apikey={bscscan_api_key}"

    try:
        response = requests.get(bscscan_url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes

        result = response.json()
        token_transfers = result["result"]

        for transfer in token_transfers:
            token_symbol = transfer["tokenSymbol"]
            if token_symbol == NIAO_TOKEN_SYMBOL:
                return True

        # Check if there are more pages of results
        page_count = int(result["page"])
        total_pages = int(result["total_pages"])

        while page_count < total_pages:
            page_count += 1
            bscscan_url = f"https://api.bscscan.com/api?module=account&action=tokentx&address={wallet_address}&startblock=0&endblock=999999999&sort=asc&page={page_count}&offset=10000&apikey={bscscan_api_key}"
            response = requests.get(bscscan_url)
            response.raise_for_status()

            result = response.json()
            token_transfers = result["result"]

            for transfer in token_transfers:
                token_symbol = transfer["tokenSymbol"]
                if token_symbol == NIAO_TOKEN_SYMBOL:
                    return True

    except requests.exceptions.RequestException as e:
        print(f"Error occurred during API request: {e}")
        # Handle the error appropriately (e.g., log, retry, or raise)

    return False

if __name__ == '__main__':
    s = has_interact_with_niao("0x1353db62F2eB3566E45518249699298A675422ae", bsc_api_key)
    print(s)