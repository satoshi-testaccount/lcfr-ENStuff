# ENSBuy
Buy ENS Names via script, Create &amp; Submit commitments for desired ENS.

```
export ACCOUNT_KEY="YOUR_PRIVATEKEY_HERE_XXXXXXXXXXXXXX"
export INFURA_KEY="YOUR_INFURA_KEY"
```

```
$ python ENSBuy.py --help
usage: ENSBuy.py [-h] [--name TARGET_NAME] [--makecommitment MAKE_COMMITMENT] [--commit SEND_COMMITMENT] [--buy_wsalt BUY_NAME] [--duration DURATION] [--auto AUTOPILOT]

ENSBuyer - lcfr.eth (1/2022)

optional arguments:
  -h, --help            show this help message and exit
  --name TARGET_NAME    Target ENS name to purchase or submit commitment for.
  --makecommitment MAKE_COMMITMENT
                        Generate a salt & commitment for a desired ENS name.
  --commit SEND_COMMITMENT
                        Broadcast generated commitment string to the network for desired ENS name.
  --buy_wsalt BUY_NAME  Broadcast purchase transaction to the network for desired ENS name, requires pre-commitment. Argument is the salt value used for commitment.
  --duration DURATION   How long to register a name for, default = 1Year
  --auto AUTOPILOT      Autopilot purchases a desired ENS name and performs all the steps automatically

python ENSBuy.py --name lcfr --makecommitment=1
[+] Generating commitment for lcfr
[+] Salt: 0x285cf16769b1689fa08948439eaf3d20559294c21650be95502442530cd7b8bb
[+] commitment : 0x03d3a120803b9f9d53fdc1728f7c9e554aa98836db200335aea12f8d4e0c6e3d 

$ python ENSBuy.py --commit 0x03d3a120803b9f9d53fdc1728f7c9e554aa98836db200335aea12f8d4e0c6e3d
[+] Sending commit transaction to the network
[+] commitment: 0x03d3a120803b9f9d53fdc1728f7c9e554aa98836db200335aea12f8d4e0c6e3d
Send transaction? y
[+] tx hash 0xcc5a9df096f41295b009d2da54c3aef5a85137e62de3a5486008f997a3776076 
[+] waiting on transaction to be mined
[+] transaction has been mined

python ENSBuy.py --name lcfr --buy_wsalt 0x285cf16769b1689fa08948439eaf3d20559294c21650be95502442530cd7b8bb
[+] Fetching ENS purchase price
[+] Price: 0.054810
[+] Sending Register transaction to the network
Send transaction? y
[+] tx hash 0x61ad5c373ec034b6a3ea418aa33c80ba5a13df6b297d4c98a5e6e1493283d165 
[+] transaction was mined


$ python ENSBuy.py --name imajin --autopilot=1
[+] Generating commitment for imajin
[+] Salt: 0x9ed3fe780a1672dc77dcbf45f642caf1c00cf2ef3ddd995f90012d7af54bf2d1
[+] commitment : 0xf45bcf7147544148513cc2deaf57a221349657153c6858b5ef3cb5e16ddefa40 
[+] Sending commit transaction to the network
[+] commitment: b'\xf4[\xcfqGTAHQ<\xc2\xde\xafW\xa2!4\x96W\x15<hX\xb5\xef<\xb5\xe1m\xde\xfa@'
Send transaction? y
[+] tx hash 0x8edc1c93149827d48f7595a875d7238fa306b48e2a82f44be28c5f8115f84811 
[+] waiting on transaction to be mined
[+] transaction has been mined
[+] waiting 60 seconds ..
[+] Fetching ENS purchase price
[+] Price: 0.001713
[+] Sending Register transaction to the network
Send transaction? y
[+] tx hash 0x0aadbb8507e49b401f551916b45abf0f6f6df35794ad468d4837f1cec0205d57 
[+] transaction was mined

```
