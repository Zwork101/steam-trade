import asyncio
import pytrade
import json

# Open a premade prices file.
# In this example the file is set up like this:
# {"name": {"sell": {"metal": 1, "keys": 2}, "buy": {"metal": 0, "keys": 1}}}
with open("prices.json", "r") as f:
    prices = json.load(f)

steam_client = pytrade.login.AsyncClient('name', 'pass', shared_secret='secret')
trade_manager = pytrade.manager_trade.TradeManager('steam 64 id', key='apikey', identity_secret='your other secret')
global_manager = pytrade.GlobalManager([trade_manager])


# Client has logged in
@trade_manager.on('logged_on')
async def login():
    print('Logged in!')


# A new trade has been received. Gives an EconTradeOffer.TradeOffer object
@trade_manager.on('new_trade')
async def new_offer(trade_offer):
    print(f"Got Offer: {trade_offer.tradeofferid}")
    losing_metal = 0
    losing_keys = 0
    gaining_metal = 0
    gaining_keys = 0

    decline = False

    for item in trade_offer.items_to_receive:
        # Get the name of the item
        # Please note - in a production bot you should NEVER just use the market name of the item
        # This name excludes lots of important information (such as craftability, unusual etc)
        # You can use the pytf2 module's st_item_to_str method to convert this to a safer name
        # See https://github.com/mninc/pytf#st_item_to_stritem for more info
        name = item.market_name

        if name in prices:
            gaining_keys += prices[name]["buy"]["keys"]
            gaining_metal += prices[name]["buy"]["metal"]
        else:
            # We haven't set a price for this item. Let's decline the offer
            decline = True

    for item in trade_offer.items_to_give:
        name = item.market_name
        if name in prices:
            losing_keys += prices[name]["sell"]["keys"]
            losing_metal += prices[name]["sell"]["metal"]
        else:
            decline = True

    if decline:
        await trade_offer.decline()
    elif losing_metal <= gaining_metal and losing_keys <= gaining_keys:
        # This offer isn't going to lose us money - let's accept
        # Please note that a production bot should really convert some keys to ref if this is False
        # Otherwise banking items on a key boundary (eg sell for 2 keys, buy for 1 key 35 ref) will not work
        response = await trade_offer.accept()
        if response[0]:
            print("Accepted trade")
        else:
            print(f"Failed to accept trade: {response[1]}")

# This is the basic setup for the program, and it will run forever. Currently, there is no "nice" way to end it.
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.ensure_future(trade_manager.login(steam_client)))
global_manager.run_forever()
