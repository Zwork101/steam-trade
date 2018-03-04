import asyncio
from pytrade import login, client

steam_cli = login.AsyncClient('name', 'pass', shared_secret='secret')
manager = client.TradeManager('steam 64 id', key='apikey', identity_secret='your other secret')


# This will be called, when it completes the client.login
@manager.on('logged_on')
async def login():
    print('Logged in!')


# On a new trade, this will be called. an EconTradeOffer.TradeOffer object will be passed in
@manager.on('new_trade')
async def new_offer(trade_offer):
    print(f"Got Offer: {trade_offer.tradeofferid}")
    if not trade_offer.items_to_give:  # Not losing any items
        response = await trade_offer.accept()
        if response[0]:
            print("Accepted trade!")
        else:
            print(f"Failed to accept trade: {response[1]}")
    else:
        response = await trade_offer.decline()
        if response[0]:
            print("Declined trade!")
        else:
            print(f"Failed to decline trade: {response[1]}")


# This is the basic setup for the program, and it will run forever. Currently, there is no "nice" way to end it.
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.ensure_future(manager.login(steam_cli)))
manager.run_forever()
