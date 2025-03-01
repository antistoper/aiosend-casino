from aiocryptopay import AioCryptoPay, Networks
import config
crypto = AioCryptoPay(config.CRYPTO_TOKEN, Networks.TEST_NET)

async def get_balance():
    balances = list(await crypto.get_balance())
    return {"USDT": balances[0].available, 
            "TON": balances[1].available}

async def get_hold():
    balances = list(await crypto.get_balance())
    return {"USDT": balances[0].onhold, 
            "TON": balances[1].onhold}