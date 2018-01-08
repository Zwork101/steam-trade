# steam-trade
### An asynchronous, event based python steam trade lib
## Description

Steam-Trade is an asynchronous, event based, python steam trade library. It uses the python port `pyee` of EventEmitter, so you can focus on processing trades, and not fetching for them and parsing them! 

It's **asynchronous**, so that means it can do multiple tasks at the same time! What does this mean for you? What that means, if you get multiple trades at once, it can work on all of them at the same time. This is for total efficiency, and it's easy to work with!

It's **event based**, so that means you won't have code, doing loops, polling for trades, we do all that for you. All you have to write is a listener `@manager.on('new_trade')` and your function to proccess the event.

## Installation
You'll need to install this through pip, Python's package manager. If you don't have pip installed, then you aren't using the lastest version of python needed to run this program.
```bash
pip install -U steam-trade
```
Then, you will access it under a different name when importing it:
```py
from pytrade import *
```
## Usage
First, you will need to create an *AsyncClient* object, and a *TradeManager* object (see why the AsyncClient object is required in **FAQ**)
```py
steam_login = login.AsyncClient("Zwork101", "abc123", "super-secret-secret")
trade_manager = client.TradeManager("12345678", "steam api key", identity_secret="also-super-secret")
```
Now, run "setup" code. Code, like reading a database, or getting prices from a site. This code will only be run once. For example, I might to something like:
```py
key_price = 0
with open('key_price.txt') as file:
  key_price = float(file.read())
```
After that, create coroutines to proccess events. Use `async` before `def` to expalin to python that function is a coroutine. Then, write the code to proccess these events.
```py
@manager.on('logged_on')
async def login():
  print("Trade Manager is logged in")

@manager.on('trade_accepted')
async def trade_accept(trade_offer):
    print('----NEW TRADE ACCEPTED-----------')
    print(f'Trade Offer Id: {trade_offer.tradeofferid}')
    print(f'From User: {trade_offer.steamid_other.toString()}')
    print('---------------------------------')
 ```
 Then, you need to run the program forever. Currently, there is no "clean" way to exit.
 ```py
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.ensure_future(manager.login(steam_login)))
trade_manager.run_forever()
```
## FAQ
 **Q**: Why have a class, just for a steam login?
 
 **A**: Later on, I plan on making more of these steam libraries, and they will all take AsyncClient as input
 
 **Q**: What if I want to use the program, and not run it forever?
 
 **A**: You will have to use asyncio.ensure_future(function you want to use) for each coroutine, unless you call it in another coroutine.
 
 **Q**: How can I contribute?
 
 **A**: There are lots of ways! Just by uploading an example, or data to sample from is helpful!
