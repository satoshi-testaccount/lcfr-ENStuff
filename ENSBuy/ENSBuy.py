 from web3 import Web3, HTTPProvider
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.middleware import geth_poa_middleware

import argparse, time, random, os, json


class ENSBuy:
    def __init__(self, args):
        self.test_net = args.test_net

        self.target = args.target_name
        self.commitment = args.make_commitment
        self.commit = args.send_commitment
        self.buy_name_salt = args.buy_name
        self.duration = 31556952 * args.duration # 1 year
        self.autopilot = args.autopilot

        self.pk_key = os.getenv("ACCOUNT_KEY")
        self.infura_key = os.getenv("INFURA_KEY")

        self.ETH_ACCOUNT: LocalAccount = Account.from_key(self.pk_key)
        self.ENS_REGISTRAR_CONTROLLER = "0x283af0b28c62c092c9727f1ee09c02ca627eb7f5"
        if self.test_net:
            provider = f"https://goerli.infura.io/v3/{self.infura_key}"
        else:
            provider = f"https://mainnet.infura.io/v3/{self.infura_key}"

        self.w3 = Web3(HTTPProvider(provider))
        self.w3.eth.default_account = self.ETH_ACCOUNT.address

        if self.test_net:
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            self.w3.middleware_onion.add(construct_sign_and_send_raw_middleware(self.ETH_ACCOUNT))

        # to lazy to pull only the functions ABI's we need.
        self.abi_json = json.loads(open('./abi/'+self.ENS_REGISTRAR_CONTROLLER + '.json', 'r').read())
        self.ENS = self.w3.eth.contract(address=self.w3.toChecksumAddress(self.ENS_REGISTRAR_CONTROLLER), abi=self.abi_json)

    def make_commitment(self):
        print("[+] Generating commitment for %s" % self.target)
        salt = self.w3.toHex(random.getrandbits(256))
        print("[+] Salt: %s" % salt)
        commitment = self.ENS.functions.makeCommitment(self.target, self.ETH_ACCOUNT.address, salt).call()
        print("[+] commitment : %s " % self.w3.toHex(commitment))
        return [salt, commitment]

    def send_commitment(self, commitment):
        print("[+] Sending commit transaction to the network")
        print("[+] commitment: %s" % commitment)
        verify = input("Send transaction? ")
        nonce = self.w3.eth.getTransactionCount(self.ETH_ACCOUNT.address)
        if verify == "y":
            tx_info = self.ENS.functions.commit(commitment).buildTransaction() #transact()
            tx_info['nonce'] = nonce
            signed_tx = self.w3.eth.account.sign_transaction(tx_info, self.pk_key)
            commit_tx = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print("[+] tx hash %s " % self.w3.toHex(commit_tx))
            print("[+] waiting on transaction to be mined")
            self.w3.eth.wait_for_transaction_receipt(commit_tx)
            print("[+] transaction has been mined")
        else:
            exit("[-] transaction cancelled")

    def buy_name(self, salt):
        print("[+] Fetching ENS purchase price")
        price = self.ENS.functions.rentPrice(self.target, self.duration).call()
        print("[+] Price: %f" % price)
        print("[+] Sending Register transaction to the network.")
        verify = input("Send transaction? ")
        if verify == "y":
            tx_info = self.ENS.functions.register(
                self.target,
                self.ETH_ACCOUNT.address,
                self.duration,
                salt
            ).buildTransaction({'value': self.w3.toWei(price, "wei")})
            nonce = self.w3.eth.getTransactionCount(self.ETH_ACCOUNT.address)
            tx_info['nonce'] = nonce
            signed_tx = self.w3.eth.account.sign_transaction(tx_info, self.pk_key)
            register_transaction = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print("[+] tx hash %s " % self.w3.toHex(register_transaction))
            self.w3.eth.wait_for_transaction_receipt(register_transaction)
            print("[+] transaction was mined")
        else:
            exit("[-] transaction cancelled")

    def main(self):
        if not self.pk_key:
            exit("[-] No private key provided for transactions")
        if not self.infura_key:
            exit("[-] No infura key provided to relay transactions")

        if self.commitment:
            if not self.target:
                exit("[-] No target ENS name provided - needed to generate commitment or purchase.")
            self.make_commitment()

        if self.commit:
            self.send_commitment(self.commit)

        if self.buy_name_salt:
            if not self.target:
                exit("[-] No target ENS name provided - needed to generate commitment or purchase.")
            self.buy_name(self.buy_name_salt)

        if self.autopilot:
            if not self.target:
                exit("[-] No target ENS name provided - needed to generate commitment or purchase.")
            commitment = self.make_commitment()
            self.send_commitment(commitment[1])
            time.sleep(62)
            self.buy_name(commitment[0])

        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ENSBuyer - lcfr.eth (1/2022)\n")
    parser.add_argument("--name", dest="target_name", type=str,
                        help="Target ENS name to purchase or submit commitment for.",
                        default=None)

    parser.add_argument("--makecommitment", dest="make_commitment", action='store_true',
                        help="Generate a salt & commitment for a desired ENS name.",
                        default=False)

    parser.add_argument("--commit", dest="send_commitment", type=str,
                        help="Broadcast generated commitment string to the network for desired ENS name.",
                        default=None)

    parser.add_argument("--buy_wsalt", dest="buy_name", type=str,
                        help="Broadcast purchase transaction to the network for desired ENS name, requires "
                             "pre-commitment. Argument is the salt value used for commitment.",
                        default=None)

    parser.add_argument("--duration", dest="duration", type=int,
                        help="How long to register a name for, default = 1 Year",
                        default=1)

    parser.add_argument("--autopilot", dest="autopilot", action='store_true',
                        help="Autopilot purchases a desired ENS name and performs all the steps automatically",
                        default=False)

    parser.add_argument("--testnet", dest="test_net", action='store_true',
                        help="Enable Testnet",
                        default=False)

    args = parser.parse_args()
    x = ENSBuy(args)
    x.main()
