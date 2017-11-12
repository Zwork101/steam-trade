import asyncio
from pytrade import login, client

steam_cli = login.AsyncClient('name', 'pass', shared_secret="secret")
manager = client.TradeManager('steam 64 id', key='apikey', identity_secret="your other secret")

# This will be called, when it completes the client.login
@manager.on('logged_on')
async def login():
    print('Logged in!')

# On a new trade, this will be called. an EconTradeOffer.TradeOffer object will be passed in
@manager.on('new_trade')
async def new_offer(trade_offer):
    print(f"Got Offer: {trade_offer.tradeofferid}")
    if trade_offer.steamid_other.toString() == manager.steamid.toString():
        print("This offer is from us! Accepting")
        await trade_offer.accept()
    else:
        print("Not from us, declining")
        await trade_offer.decline()

# This is called at the end of polling
@manager.on('end_poll')
async def poll_end():
    print("Poll ended.")

# This is called at the start of polling
@manager.on('start_poll')
async def poll_start():
    print("Poll started")

# This is called when a trade is accepted
@manager.on('trade_accepted')
async def accepted_offer(trade_offer):
    print(f"Accepted Offer: {trade_offer.tradeofferid}")

# This is the basic setup for the program, and it will run forever. Currently, there is no "nice" way to end it.
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.ensure_future(manager.login(steam_cli)))
manager.run_forever()