from const import *


class Trade:
    def __init__(self, dex_name_, price_, size_, side_, timestamp_):
        self.dex_name: DexName = dex_name_
        self.price: float = price_
        self.size: float = size_
        self.side: Side = side_
        self.timestamp: int = timestamp_

    def __str__(self):
        return (
            f'DEX: {self.dex_name} | PRICE: {self.price} | SIZE: {self.size} | SIDE: {self.side} | TIME: {self.timestamp}')


def arr_to_txt(arr, filename='txs.txt'):
    with open(filename, 'a') as f:
        for el in arr:
            f.write('NEW BLOCK\n')
            f.write('BUY\n')
            if len(el[Side['Buy']]) > 1:
                for x in el[Side['Buy']]:
                    f.write(str(x) + '\n')
            f.write('SELL\n')
            if len(el[Side['Sell']]) > 1:
                for x in el[Side['Sell']]:
                    f.write(str(x) + '\n')
            f.write('------------------------------------------------------\n')


def convert_usdt(amount: int) -> float:
    return amount / 10. ** 6


def parse_swaps(tx_hash) -> List[Trade]:
    try:
        receipt = w3.eth.getTransactionReceipt(tx_hash)
        decoded_logs = weth_usdt_uniswap_v2_contract.events.Swap().processReceipt(receipt)
        return [parse_log(log) for log in decoded_logs]
    except web3.exceptions.MismatchedABI:
        pass


def check_dex(log) -> DexName:
    if log['address'] == WETH_USDT_UNISWAP_ADDR:
        return DexName['Uniswap']
    if log['address'] == WETH_USDT_SUSHISWAP_ADDR:
        return DexName['Sushiswap']


cache_n = 0
cache_timestamp = 0


def parse_log(log) -> Trade:
    global cache_n, cache_timestamp
    dex_name_ = check_dex(log)
    if check_dex(log):
        data = log['args']
        weth_in = w3.fromWei(data['amount0In'], 'ether')
        usdt_in = convert_usdt(data['amount1In'])
        weth_out = w3.fromWei(data['amount0Out'], 'ether')
        usdt_out = convert_usdt(data['amount1Out'])

        side_ = Side['Sell'] if weth_out > 0 else Side['Buy']
        size_ = weth_in + weth_out
        price_ = decimal.Decimal(usdt_out + usdt_in) / (weth_out + weth_in)
        if log['blockNumber'] == cache_n:
            timestamp_ = cache_timestamp
        else:
            timestamp_ = w3.eth.getBlock(log['blockNumber']).timestamp
            cache_n = log['blockNumber']
            cache_timestamp = timestamp_

        return Trade(dex_name_, price_, size_, side_, timestamp_)


def get_event_history(dex_name) -> List[Dict]:
    if dex_name == DexName['Uniswap']:
        return weth_usdt_uniswap_v2_contract.events.Swap.getLogs(fromBlock=(w3.eth.get_block_number() - 1000))
    if dex_name == DexName['Sushiswap']:
        return weth_usdt_sushiswap_contract.events.Swap.getLogs(fromBlock=(w3.eth.get_block_number() - 1000))
    raise ValueError


def process_swap_events(logs) -> List[Trade]:
    return [parse_log(log) for log in logs]


def main():
    uniswap_event_history = get_event_history(DexName['Uniswap'])
    print('Uniswap history loaded')
    sushiswap_event_history = get_event_history(DexName['Sushiswap'])
    print('Sushiswap history loaded')
    uni_trades = process_swap_events(uniswap_event_history)
    sushi_trades = process_swap_events(sushiswap_event_history)
    print('Timestamps loaded')

    blocks = []
    i = 0
    j = 0
    while i < len(uni_trades) and j < len(sushi_trades):
        block = {
            Side['Sell']: [],
            Side['Buy']: []
        }

        block_timestamp = max(uni_trades[i].timestamp, sushi_trades[j].timestamp)

        if uni_trades[i].timestamp == sushi_trades[j].timestamp:
            while i < len(uni_trades) and uni_trades[i].timestamp == block_timestamp:
                block[uni_trades[i].side].append(uni_trades[i])
                i += 1
            while j < len(sushi_trades) and sushi_trades[j].timestamp == block_timestamp:
                block[sushi_trades[j].side].append(sushi_trades[j])
                j += 1

        while i < len(uni_trades) and uni_trades[i].timestamp < block_timestamp:
            # block[uni_trades[i].side].append(uni_trades[i])
            i += 1

        while j < len(sushi_trades) and sushi_trades[j].timestamp < block_timestamp:
            # block[sushi_trades[j].side].append(sushi_trades[j])
            j += 1

        if len(block[Side['Sell']]) > 1 or len(block[Side['Buy']]) > 1:
            blocks.append(block)

    print('Check txs.txt for results')
    return blocks


if __name__ == "__main__":
    result = main()
    arr_to_txt(result)
