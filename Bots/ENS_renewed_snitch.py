from web3 import Web3, HTTPProvider
import time
import json
import os

INFURA_KEY = os.getenv("INFURA_KEY")

ENS_REGISTRAR_CONTROLLER = "0x283af0b28c62c092c9727f1ee09c02ca627eb7f5"
w3 = Web3(HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_KEY}"))

abi_json = json.loads(open('./abi/' + ENS_REGISTRAR_CONTROLLER + '.json', 'r').read())
ENS = w3.eth.contract(address=w3.toChecksumAddress(ENS_REGISTRAR_CONTROLLER), abi=abi_json)


def handle_event(event):
    tx_hash = w3.toHex(event["transactionHash"])
    tx_details = w3.eth.get_transaction(tx_hash)
    name = event['args']['name']
    from_address = tx_details['from']
    print(f"[+] {name}.eth renewed at tx: {tx_hash} by: {from_address}")


def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        time.sleep(poll_interval)


def main():
    block_filter = ENS.events.NameRenewed.createFilter(fromBlock='latest')
    log_loop(block_filter, 2)


if __name__ == '__main__':
    main()
