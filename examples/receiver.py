# NOT UPDATED

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


# A new confirmation (including ones that are going to be accepted automatically)
@manager.on('new_conf')
async def new_conf(conf):
    print(f"Got confirmation: {conf.id}")


# This is called at the end of polling
@manager.on('end_poll')
async def poll_end():
    print("Poll ended.")


# This is called at the start of polling
@manager.on('start_poll')
async def poll_start():
    print("Poll started.")


# This is called when there is an error in some of your code
@manager.on('error')
async def error(message):
    print(f"Our code errored: {message}")


# This is called when there is an error whilst polling.
# This should be caught and polling will continue as normal
@manager.on('poll_error')
async def poll_error(message):
    print(f"Poll error: {message}")


# This is called when a trade is accepted
@manager.on('trade_accepted')
async def accepted_offer(trade_offer):
    print(f"Accepted Offer: {trade_offer.tradeofferid}")


# This is called when a trade is declined
@manager.on('trade_declined')
async def declined_offer(trade_offer):
    print(f"Declined Offer: {trade_offer.tradeofferid}")


# This is called when a trade is cancelled
@manager.on('trade_canceled')
async def canceled_offer(trade_offer):
    print(f"Canceled Offer: {trade_offer.tradeofferid}")


# This is called when a trade has expired
@manager.on('trade_expired')
async def expired_offer(trade_offer):
    print(f"Expired Offer: {trade_offer.tradeofferid}")


# This is called when a trade has been countered
@manager.on('trade_countered')
async def countered_offer(trade_offer):
    print(f"Countered Offer: {trade_offer.tradeofferid}")


# This is called when a trade state has changed to something unexpected
@manager.on('trade_state_changed')
async def changed_offer(trade_offer):
    print(f"Countered Offer: {trade_offer.tradeofferid}")

# This is the basic setup for the program, and it will run forever. Currently, there is no "nice" way to end it.
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.ensure_future(manager.login(steam_cli)))
manager.run_forever()
