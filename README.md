# steam-trade

### An asynchronous, event based python steam trade lib
## Description

Steam-Trade is an asynchronous, event based, python steam trade library. It uses the python port `pyee` of EventEmitter, so you can focus on processing trades, and not fetching for them and parsing them! 

It's **asynchronous**, so that means it can do multiple tasks at the same time! What does this mean for you? What that means, if you get multiple trades at once, it can work on all of them at the same time. This is for total efficiency, and it's easy to work with!

It's **event based**, so that means you won't have code, doing loops, polling for trades, we do all that for you. All you have to write is a listener `@manager.on('new_trade')` and your function to proccess the event.

## Installation
You'll need to install this through pip, Python's package manager. If you don't have pip installed, then reinstall python with the install pip option checked (It's possible other ways, but this is seriously the easiest).
If you're installing python via a linux command line and pip isn't available, try running `sudo apt install python3-pip`.

Do `pip install -U steam-trade`, or if pip isn't added to path do `python -m pip install -U steam-trade`, substituting python with whatever you use to run python3.6 normally (this differs if you have another version of python installed)

Then, you will access it under a different name when importing it:
```py
import pytrade
```
## Usage
First, you will need to create an *AsyncClient* object, and a *TradeManager* object (see why the AsyncClient object is required in **FAQ**)
```py
steam_login = pytrade.login.AsyncClient("Zwork101", "abc123", shared_secret="super-secret-secret")
trade_manager = pytrade.manager_trade.TradeManager("12345678", "steam api key", identity_secret="also-super-secret")
global_manager = pytrade.GlobalManager([trade_manager])
```

Now, run any setup code you want.

After that, create coroutines to proccess events. Use `async` before `def` to expalin to python that function is a coroutine. Then, write the code to proccess these events.
```py
@trade_manager.on('logged_on')
async def login():
  print("Trade Manager is logged in")

@trade_manager.on('trade_accepted')
async def trade_accept(trade_offer):
    print('----NEW TRADE ACCEPTED-----------')
    print(f'Trade Offer Id: {trade_offer.tradeofferid}')
    print(f'From User: {trade_offer.steamid_other.toString()}')
    print('---------------------------------')
```
Then, you need to run the program forever. Currently, there is no "clean" way to exit.
```py
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.ensure_future(trade_manager.login(steam_login)))
global_manager.run_forever()
```
## FAQ
 **Q**: Why have a class just for a steam login? Why is there a global manager and a trade manager? Why does the global manager take the trade manager in a list?
 
 **A**: Futureproofing. The global manager should be able to take many more modules, not just a trade manager. This makes it easy to add something like a steam chat manager in the future.
 
 **Q**: What if I want to use the program, and not run it forever?
 
 **A**: You will have to use `asyncio.ensure_future(function you want to use)` for each coroutine, unless you call it in another coroutine. Each manager has a `poll` method, you could run that when you like.
 
 **Q**: How can I help?
 
 **A**: There are lots of ways! Upload an example, rewrite some code (make sure to check it works first!), send a donation or just star the project - it is all appreciated!

 **Q**: Who the hell made this *amazing* library?!?

 **A**: Check out the [contibutors tab](https://github.com/Zwork101/steam-trade/graphs/contributors)!