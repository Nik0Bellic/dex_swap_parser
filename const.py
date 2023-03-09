from web3 import Web3
from enum import Enum
import decimal
from typing import List, Dict
import web3.exceptions

MAINNET_PROVIDER = "http://moonbears.trippynode.xyz:8545/"
w3 = Web3(Web3.HTTPProvider(MAINNET_PROVIDER))

WETH_USDT_ABI = [{"anonymous": False,
                  "inputs": [
                      {"indexed": True,
                       "internalType": "address",
                       "name": "sender",
                       "type": "address"},
                      {"indexed": False,
                       "internalType": "uint256",
                       "name": "amount0In",
                       "type": "uint256"},
                      {"indexed": False,
                       "internalType": "uint256",
                       "name": "amount1In",
                       "type": "uint256"},
                      {"indexed": False,
                       "internalType": "uint256",
                       "name": "amount0Out",
                       "type": "uint256"},
                      {"indexed": False,
                       "internalType": "uint256",
                       "name": "amount1Out",
                       "type": "uint256"},
                      {"indexed": True,
                       "internalType": "address",
                       "name": "to",
                       "type": "address"}],
                  "name": "Swap",
                  "type": "event"}]
WETH_USDT_UNISWAP_ADDR = w3.toChecksumAddress('0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852')
WETH_USDT_SUSHISWAP_ADDR = w3.toChecksumAddress('0x06da0fd433C1A5d7a4faa01111c044910A184553')
weth_usdt_uniswap_v2_contract = w3.eth.contract(address=WETH_USDT_UNISWAP_ADDR, abi=WETH_USDT_ABI)
weth_usdt_sushiswap_contract = w3.eth.contract(address=WETH_USDT_SUSHISWAP_ADDR, abi=WETH_USDT_ABI)

SWAP_TOPIC = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
TEST_TX_HASH = "0x458fea24d01647429bc5e16e275487ed8b375eb2599f40abd92436b7d3db9942"

DexName = Enum('DexName', ['Uniswap', 'Sushiswap'])
Side = Enum('Side', ['Buy', 'Sell'])
