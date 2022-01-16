from web3 import Web3, HTTPProvider
from eth_account import Account
from eth_account.signers.local import LocalAccount
import time, json, os


INFURA_KEY = os.getenv("INFURA_KEY")
ENS_REGISTRAR_CONTROLLER = "0x283af0b28c62c092c9727f1ee09c02ca627eb7f5"

w3 = Web3(HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_KEY}"))
abi_json = json.loads(open(ENS_REGISTRAR_CONTROLLER + '.json', 'r').read())
ENS = w3.eth.contract(address=w3.toChecksumAddress(ENS_REGISTRAR_CONTROLLER), abi=abi_json)


def handle_event(event):
    print("[+] %s.eth registered by %s" % (event["args"]["name"], event["args"]["owner"]))


def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        time.sleep(poll_interval)


def main():
    block_filter = ENS.events.NameRegistered.createFilter(fromBlock='latest')
    log_loop(block_filter, 2)
    

if __name__ == '__main__':
    main()
