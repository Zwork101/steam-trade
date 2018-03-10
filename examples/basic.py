import asyncio
import pytrade
from pytrade import login, manager_trade

steam_client = login.AsyncClient('name', 'pass', shared_secret='secret')
trade_manager = manager_trade.TradeManager('steam 64 id', key='apikey', identity_secret='your other secret')
global_manager = pytrade.GlobalManager([trade_manager])


@global_manager.on('logged_on')
async def login():
    print('Logged in!')


@global_manager.on('new_trade')
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


loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.ensure_future(trade_manager.login(steam_client)))
global_manager.run_forever()
