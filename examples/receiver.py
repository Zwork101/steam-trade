# NOT UPDATED

import asyncio
import pytrade

steam_client = pytrade.login.AsyncClient('name', 'pass', shared_secret='secret')
trade_manager = pytrade.manager_trade.TradeManager('steam 64 id', key='apikey', identity_secret='your other secret')
global_manager = pytrade.GlobalManager([trade_manager])


# This will be called, when it completes the client.login
@trade_manager.on('logged_on')
async def login():
    print('Logged in!')


# On a new trade, this will be called. an EconTradeOffer.TradeOffer object will be passed in
@trade_manager.on('new_trade')
async def new_offer(trade_offer):
    print(f"Got Offer: {trade_offer.tradeofferid}")


# A new confirmation (including ones that are going to be accepted automatically)
@trade_manager.on('new_conf')
async def new_conf(conf):
    print(f"Got confirmation: {conf.id}")


# This is called at the end of global polling
@trade_manager.on('global_end_poll')
async def poll_end():
    print("Global poll ended.")


# This is called at the start of global polling
@trade_manager.on('global_start_poll')
async def poll_start():
    print("Global poll started.")


# This is called at the end of trade polling
@trade_manager.on('trade_end_poll')
async def poll_end():
    print("Trade poll ended.")


# This is called at the start of trade polling
@trade_manager.on('trade_start_poll')
async def poll_start():
    print("Trade poll started.")


# This is called when there is an error in some of your code
@trade_manager.on('error')
async def error(message):
    print(f"Our code errored: {message}")


# This is called when there is an error whilst polling.
# This should be caught and polling will continue as normal
@trade_manager.on('trade_poll_error')
async def poll_error(message):
    print(f"Poll error: {message}")


# This is called when a trade is accepted
@trade_manager.on('trade_accepted')
async def accepted_offer(trade_offer):
    print(f"Accepted Offer: {trade_offer.tradeofferid}")


# This is called when a trade is declined
@trade_manager.on('trade_declined')
async def declined_offer(trade_offer):
    print(f"Declined Offer: {trade_offer.tradeofferid}")


# This is called when a trade is cancelled
@trade_manager.on('trade_canceled')
async def canceled_offer(trade_offer):
    print(f"Canceled Offer: {trade_offer.tradeofferid}")


# This is called when a trade has expired
@trade_manager.on('trade_expired')
async def expired_offer(trade_offer):
    print(f"Expired Offer: {trade_offer.tradeofferid}")


# This is called when a trade has been countered
@trade_manager.on('trade_countered')
async def countered_offer(trade_offer):
    print(f"Countered Offer: {trade_offer.tradeofferid}")


# This is called when a trade state has changed to something unexpected
@trade_manager.on('trade_state_changed')
async def changed_offer(trade_offer):
    print(f"Countered Offer: {trade_offer.tradeofferid}")

# This is the basic setup for the program, and it will run forever. Currently, there is no "nice" way to end it.
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.ensure_future(trade_manager.login(steam_client)))
global_manager.run_forever()
