from web3 import Web3
import abi
import time
import getpass

bsc = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(bsc))

pbladdress = web3.toChecksumAddress(str(input("Enter your public address: ")))
prvaddress = str(getpass.getpass("Enter your private key (dont worry she will not be stored): "))

pancakeRouterAddress = '0x10ED43C718714eb63d5aA57B78B54704E256024E'
wbnbAddress = web3.toChecksumAddress("0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c")

def getAllowance(_tokenaddress):
    erc20_contract = web3.eth.contract(address=_tokenaddress, abi=abi.erc20ABI)
    return erc20_contract.functions.allowance(pbladdress, pancakeRouterAddress).call()

def getDecimals(_tokenaddress):
    erc20_contract = web3.eth.contract(address=_tokenaddress, abi=abi.erc20ABI)
    return erc20_contract.functions.decimals().call()

def getBalance(_walletaddress, _tokenaddress):
    erc20_contract = web3.eth.contract(address=_tokenaddress, abi=abi.erc20ABI)
    return erc20_contract.functions.balanceOf(_walletaddress).call()

def getSymbol(_tokenaddress):
    erc20_contract = web3.eth.contract(address=_tokenaddress, abi=abi.erc20ABI)
    return erc20_contract.functions.symbol().call()


def balanceReadable(_token, _balance):
    decimals = getDecimals(_token)
    humanbalance = _balance/10**decimals
    return humanbalance


def approveToken(_token, _amount):
    print("approving token to pancakeswap... (~10sec)")
    erc20_contract = web3.eth.contract(address=_token, abi=abi.erc20ABI)
    trx = erc20_contract.functions.approve(pancakeRouterAddress, _amount).buildTransaction({
            'from': pbladdress,
            'gas': 250000,
            'gasPrice': web3.toWei('5','gwei'),
            'nonce': web3.eth.get_transaction_count(pbladdress),
            })
    
    signed_trx = web3.eth.account.sign_transaction(trx, private_key=prvaddress)
    trx_token = web3.eth.send_raw_transaction(signed_trx.rawTransaction)
    trx_id = web3.toHex(trx_token)
    print("transaction => https://bscscan.com/tx/",trx_id)


def swapToken(_token, _amount):
    print("swapping tokens...💰")
    router_contract = web3.eth.contract(address=pancakeRouterAddress, abi=abi.pancakerouterABI)
    nonce = web3.eth.get_transaction_count(pbladdress)
    decimals = getDecimals(_token)

    trx = router_contract.functions.swapExactTokensForETH(
    _amount,
    0, 
    [_token,wbnbAddress],
    pbladdress,
    (int(time.time()) + 10000)
    ).buildTransaction({
    'from': pbladdress,
    'gas': 250000,
    'gasPrice': web3.toWei('5','gwei'),
    'nonce': nonce,
    })

    signed_trx = web3.eth.account.sign_transaction(trx, private_key=prvaddress)
    trx_token = web3.eth.send_raw_transaction(signed_trx.rawTransaction)
    trx_id = web3.toHex(trx_token)
    print("transaction advancement => https://bscscan.com/tx/",trx_id)



tokenToDump = web3.toChecksumAddress(input("Enter the token address you want to dump: ")) 
amountToDump = input("How much token do you want to dump (type 'all' if you want to sell all your tokens): ")
decimals = getDecimals(tokenToDump)
symbol = getSymbol(tokenToDump)

if amountToDump == "all":
    atd = 8000000000
else:
    atd = int(amountToDump)

if getAllowance(tokenToDump) < atd*10**decimals:
    approveToken(tokenToDump, 8000000000000000000000000000)
    time.sleep(12)
else:
    print("no need to approve, already did")


print("looking mode 👁")

while getBalance(pbladdress, tokenToDump) <= 0:
    time.sleep(1)
    print("looking", symbol, "balance 👀 (0)")

print(balanceReadable(tokenToDump, getBalance(pbladdress, tokenToDump)), symbol, "just appear in your wallet ! 🛬")

if amountToDump == "all":
    amountToDump = getBalance(pbladdress, tokenToDump)
else:
    amountToDump = int(amountToDump)*10**decimals

print("lets dump", balanceReadable(tokenToDump, amountToDump), symbol, "!")

swapToken(tokenToDump, amountToDump)
time.sleep(20)
