from web3 import Web3, HTTPProvider
import time
import json
import os
import argparse


class ENSEvents:
    def __init__(self, args):
        self.INFURA_KEY = os.getenv("INFURA_KEY")
        self.registered = args.registered_log
        self.renewed = args.renewed_log

        self.ENS_REGISTRAR_CONTROLLER = "0x283af0b28c62c092c9727f1ee09c02ca627eb7f5"
        self.w3 = Web3(HTTPProvider(f"https://mainnet.infura.io/v3/{self.INFURA_KEY}"))

        self.abi_json = json.loads(open('./abi/' + self.ENS_REGISTRAR_CONTROLLER + '.json', 'r').read())
        self.ENS = self.w3.eth.contract(address=self.w3.toChecksumAddress(self.ENS_REGISTRAR_CONTROLLER), abi=self.abi_json)


    def handle_register_event(self, event):
        name = event["args"]["name"]
        owner = event["args"]["owner"]
        ens = self.w3.ens.name(self.w3.toChecksumAddress(owner))
        if ens:
            owner = ens
        print("[+] %s.eth registered by %s" % (name, owner))
        return

    def handle_renew_event(self, event):
        tx_hash = self.w3.toHex(event["transactionHash"])
        tx_details = self.w3.eth.get_transaction(tx_hash)
        name = event['args']['name']
        from_address = tx_details['from']
        ens = self.w3.ens.name(self.w3.toChecksumAddress(from_address))
        if ens:
            from_address = ens
        print(f"\n[+] {name}.eth renewed\n-by: {from_address}\n-at tx: {tx_hash}\n")

    def log_loop(self, event_filter, poll_interval):
        while True:
            for event in event_filter.get_new_entries():
                if self.renewed and event["event"] == "NameRenewed":
                    self.handle_renew_event(event)

                if self.registered and event["event"] == "NameRegistered":
                    self.handle_register_event(event)
            time.sleep(poll_interval)

    def main(self):
        if self.renewed:
            print("[+] Streaming ENS Name Renewals")
            block_filter = self.ENS.events.NameRenewed.createFilter(fromBlock='latest')

        if self.registered:
            print("[+] Streaming ENS Name Registrations")
            block_filter = self.ENS.events.NameRegistered.createFilter(fromBlock='latest')

        self.log_loop(block_filter, 2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ENSEvents - lcfr.eth (1/2021)\n")
    parser.add_argument("--registered", dest="registered_log", type=bool,
                        help="Streams ENS Registrations live.",
                        default=True)

    parser.add_argument("--renewed", dest="renewed_log", type=bool,
                        help="Streams ENS Renewals live.",
                        default=True)
    
    args = parser.parse_args()
    ENSEvents(args).main()
