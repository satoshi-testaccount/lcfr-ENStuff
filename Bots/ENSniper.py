#!venv/bin/python3.9
"""
usage:
export NODE=http://192.168.1.139:8545
export PKEY=XXXXXXXXXXXXXXXXXXXXXXXXX

Initiate the DB for the first time, default file path is expired.db. Provide --database file.db to use non-default.
$ ENSNiper.py --init

Add a name with the desired price to the DB.
$ ENSniper.py --add lolol --price 0.006

Update the desired price of a name already existing in the DB.
$ ENSniper.py --update lolol --price 0.0666

Delete the name from the DB completely.
$ ENSniper.py --del lolol

Register the desired name: Submits commitment, waits 60 seconds and sends the register tx.
$ ENSniper.py --register goerlilol

--bot : Enable bot loop for all names/prices in DB
--testnet : Testnet enabled for --register
--duration : default is 1 year. Provide single/whole digits. Ex: 1, 2, 3, 4, 5

$ ENSniper.py --bot
[+] Connected to DB at expired.db
[+] bot running.
[+] xxxxx.eth current_price: 9.813835 desired_price: 0.xxx
[+] xxxxx.eth current_price: 19.146576 desired_price: 0.xxx
[+] xxxxx.eth current_price: 3.742025 desired_price: 0.xxx
[+] xxxxx.eth current_price: 1.796239 desired_price: 0.xxx
[+] xxxxx.eth current_price: 6.112605 desired_price: 0.xxx
[+] xxxxx.eth current_price: 20.608630 desired_price: 0.xxx
[+] xxxxx.eth current_price: 15.015172 desired_price: 0.xxx

~lcfr.eth - 03/22
"""

from web3 import Web3, HTTPProvider
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_account.signers.local import LocalAccount
from sqlite3 import Error
from ast import literal_eval

import json
import random
import argparse
import sqlite3
import time
import os


class ENSniper:
    def __init__(self, args):
        self.add_word = args.add_word
        self.target_price = args.target_price
        self.bot = args.bot
        self.update_price = args.update_price
        self.del_word = args.del_word
        self.register_name = args.register_name
        self.test_net = args.test_net
        self.database = args.database
        self.duration = args.duration * 31556952  # 31556952 : 1 year
        self.init_db = args.init_db

        # REQUIRED
        self.p_key = os.getenv("PKEY")  # private key for TX's
        self.provider = os.getenv("NODE") 
        
        # only for testnet, not required.
        self.infura_key = os.getenv("INFURA_KEY")

        if not self.p_key:
            exit("[-] export privateKey in PKEY env variable..")

        if self.test_net:
            self.provider = f"https://goerli.infura.io/v3/{self.infura_key}"
            print("[+] testnet enabled, connected to goerli infura node.")

        if not self.provider:
            exit("[-] export provider URL in NODE env variable. Local or Infura or enable testnet mode.")

        self.ETH_ACCOUNT: LocalAccount = Account.from_key(self.p_key)
        self.ENS_REGISTRAR_CONTROLLER = "0x283af0b28c62c092c9727f1ee09c02ca627eb7f5"
        self.ENS_BASE_REGISTRAR = "0x57f1887a8bf19b14fc0df6fd9b2acc9af147ea85"

        print("[+] ETH ACCOUNT: %s" % self.ETH_ACCOUNT.address)

        self.w3 = Web3(HTTPProvider(self.provider))

        if self.test_net:
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            self.w3.middleware_onion.add(construct_sign_and_send_raw_middleware(self.ETH_ACCOUNT))

        self.rc_abi_json = json.loads(open('./abi/' + self.ENS_REGISTRAR_CONTROLLER + '.json', 'r').read())
        self.br_abi_json = json.loads(open('./abi/' + self.ENS_BASE_REGISTRAR + '.json', 'r').read())

        self.ENS = self.w3.eth.contract(
            address=self.w3.toChecksumAddress(self.ENS_REGISTRAR_CONTROLLER),
            abi=self.rc_abi_json
        )
        self.ENS_REGISTRAR = self.w3.eth.contract(
            address=self.w3.toChecksumAddress(self.ENS_BASE_REGISTRAR),
            abi=self.br_abi_json
        )
        self.connection = None
        return

    def sqlite_connect(self, db_file):
        try:
            self.connection = sqlite3.connect("./DBS/" + db_file)
        except Error as e:
            exit(e)
        print(f"[+] Connected to DB at {db_file}")
        return self.connection

    def execute_sql(self, sql_statement, data=None):
        cur = self.connection.cursor()
        if data is None:
            cur.execute(sql_statement)
            result = cur.fetchall()
            return result
        else:
            cur.execute(sql_statement, data)
            self.connection.commit()
        return

    def create_db(self):
        return self.execute_sql('CREATE TABLE IF NOT EXISTS ENS(Name TEXT PRIMARY KEY, Price REAL)')

    def exists_in_db(self, name):
        statement = 'select count() from ENS where Name = "%s"' % name
        ret = self.execute_sql(statement)
        result = ret[0][0]
        if result == 0:
            return False
        else:
            return True

    def check_and_add_to_db(self, words, price):
        if len(words) < 3:
            exit("[-] ENS requires 3 letter minimal. invalid name.")

        ens_info = [words, price]
        if not self.exists_in_db(words):
            print(f"[+] Inserted {words} into DB")
            self.insert_data(ens_info)
        return

    def get_names_from_db(self):
        return self.execute_sql('select * from ENS')

    def del_names_from_db(self, name):
        self.execute_sql('DELETE from ENS where Name = ?', (name,))
        return

    def insert_data(self, data):
        self.execute_sql('INSERT INTO ENS(Name, Price) VALUES(?,?)', data)
        return

    def update_price_db(self, name, price):
        self.execute_sql('update ENS set Price = ? where Name = ?', [price, name])
        return

    #####

    def get_expiration(self, token_id):
        return self.ENS_REGISTRAR.functions.nameExpires(token_id).call()

    def derive_token_from_name(self, name):
        return literal_eval(Web3.keccak(text=name).hex())

    def check_available(self, token_id):
        return self.ENS_REGISTRAR.functions.available(token_id).call()

    def gen_salt(self):
        return self.w3.toHex(random.getrandbits(256))

    def make_commitment(self, name):
        salt = self.gen_salt()
        commitment = self.ENS.functions.makeCommitment(name, self.ETH_ACCOUNT.address, salt).call()
        return [salt, commitment]

    def commit(self, name, commitment):
        print(f"[+] sending commitment for {name}.eth")

        tx_info = self.ENS.functions.commit(commitment).buildTransaction()
        nonce = self.w3.eth.getTransactionCount(self.ETH_ACCOUNT.address)
        tx_info['nonce'] = nonce

        signed_tx = self.w3.eth.account.sign_transaction(tx_info, self.p_key)
        commit_tx = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print("[+] tx hash %s " % self.w3.toHex(commit_tx))
        print("[+] waiting on transaction to be mined")
        self.w3.eth.wait_for_transaction_receipt(commit_tx)
        print("[+] transaction mined successfully.")
        return

    def get_rent_price(self, name):
        price = self.ENS.functions.rentPrice(name, self.duration).call()
        return price

    def register(self, name, salt):
        price = self.get_rent_price(name)
        tx_info = self.ENS.functions.register(
            name,
            self.ETH_ACCOUNT.address,
            self.duration,
            salt
        ).buildTransaction({'value': price})

        nonce = self.w3.eth.getTransactionCount(self.ETH_ACCOUNT.address)
        tx_info['nonce'] = nonce
        # print(tx_info)

        signed_tx = self.w3.eth.account.sign_transaction(tx_info, self.p_key)
        register_transaction = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print("[+] tx hash %s " % self.w3.toHex(register_transaction))
        self.w3.eth.wait_for_transaction_receipt(register_transaction)
        print("[+] transaction mined successfully")
        return

    def main(self):
        self.sqlite_connect(self.database)

        if self.init_db:
            print(f"[+] initiating local DB @ {self.database}")
            self.create_db()
            return

        if self.del_word:
            print(f"[-] Removing {self.del_word}.eth from the DB")
            self.del_names_from_db(self.del_word)
            return

        if self.add_word and not self.target_price:
            print("[-] Price required for name.")
            return

        if self.add_word and self.target_price:
            print("[+] Adding %s to DB with price %f" % (self.add_word, self.target_price))
            self.check_and_add_to_db(self.add_word, self.target_price)

        if self.update_price and not self.target_price:
            print("[-] Price required for update.")
            return

        if self.update_price and self.target_price:
            name = self.update_price
            print("[+] updating price for %s.eth to %f" % (name, self.target_price))
            self.update_price_db(name, self.target_price)
            return

        if self.register_name:
            print(f"[+] weddidit -> getting {self.register_name}.eth")
            commitment_data = self.make_commitment(self.register_name)
            salt = commitment_data[0]
            print("[+] salt:", salt)
            commitment = commitment_data[1]
            print("[+] commitment:", commitment)
            # return
            self.commit(self.register_name, commitment)
            print("[+] sleeping for 60 seconds for commitment minimal duration")
            time.sleep(62)
            self.register(self.register_name, salt)

        if self.bot:
            print("[+] bot running.")
            names = self.get_names_from_db()
            while True:
                for name, price in names:
                    token_id = self.derive_token_from_name(name)
                    available = self.check_available(token_id)
                    rentprice = self.get_rent_price(name)
                    eth_price = self.w3.fromWei(rentprice, "ether")

                    print("[+] %s.eth current_price: %f desired_price: %f" % (name, eth_price, price))

                    if not available:
                        print(f"[-] {name}.eth is no longer available, removing from DB.")
                        self.del_names_from_db(name)

                    if available and eth_price <= price:
                        print(f"[+] weddidit -> getting {name}.eth")
                        commitment_data = self.make_commitment(name)
                        salt = commitment_data[0]
                        print("[+] salt:", salt)
                        commitment = commitment_data[1]
                        print("[+] commitment:", commitment)
                        self.commit(name, commitment)
                        print("[+] sleeping for 90 seconds.")
                        time.sleep(90)  # give some extra time for commitment tx to confirm. 60 flat tends to revert.
                        self.register(name, salt)

                time.sleep(120)  # "poll" delay
                print("")
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ENSniper - lcfr.eth (03/22)\n")

    parser.add_argument("--database", dest="database", type=str,
                        help="local sqlite3 database file to use, default is expired.db",
                        default='expired.db')

    parser.add_argument("--init", dest="init_db", action='store_true',
                        help="initiate new sqlite3 DB for names storage.",
                        default=False)

    parser.add_argument("--add", dest="add_word", type=str,
                        help="add list of words (1 on each line with no trailing new lines) as file.txt to the DB",
                        default=None)

    parser.add_argument("--price", dest="target_price", type=float,
                        help="Price to purchase name at or below. 0.1 will buy at 0.1 or less.",
                        default=None)

    parser.add_argument("--del", dest="del_word", type=str,
                        help="delete from DB",
                        default=None)

    parser.add_argument("--update", dest="update_price", type=str,
                        help="update desired price of name in database --price required",
                        default=None)

    parser.add_argument("--bot", dest="bot", action='store_true',
                        help="Run bot loop, checking names in DB & Price against current DutchAuctions",
                        # require fund_wallets & keys_file
                        default=False)

    parser.add_argument("--duration", dest="duration", type=int,
                        help="register name for provided duration (1, 2, 3, etc), default = 1 year",
                        default=1)

    parser.add_argument("--register", dest="register_name", type=str,
                        help="Register name - not bot mode. submits commit & register txs",
                        default=None)

    parser.add_argument("--testnet", dest="test_net", action='store_true',
                        help="Enable Testnet",
                        default=False)

    args = parser.parse_args()
    x = ENSniper(args)
    x.main()
