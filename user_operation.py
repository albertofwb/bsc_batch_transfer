from bsc_transfer import BscTransfer
from private import wallet_address


def read_address_from_file(file_path: str):
    transfer_tuple_list = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#'):
                continue
            tmp = line.split(',')
            if len(tmp) != 2:
                raise ValueError(f"Invalid address file format {line}")
            transfer_tuple_list.append(tmp)
    return transfer_tuple_list


def batch_transfer(file_path: str):
    bsc = BscTransfer()
    for addr, amount in read_address_from_file(file_path):
        bsc.transfer(wallet_address, addr, float(amount))


def auto_trade():
    from bsc_trader import BscTrader
    trader = BscTrader()
    # trader.sell(trader.token_balance)
    # trader.sell(1)
    trader.buy(1)


if __name__ == '__main__':
    auto_trade()
