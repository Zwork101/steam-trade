# steam-trade
### An asynchronous, event based python steam trade lib
## Description

Steam-Trade is an asynchronous, event based, python steam trade library. It uses the python port `pyee` of EventEmitter, so you can focus on processing trades, and not fetching for them and parsing them! 

![example](https://my-request.tk/event_new_trade.PNG "Code to accept all offers from me :D")

It's **asynchronous**, so that means it can do multiple tasks at the same time! What does this mean for you? That means, if you get multiple trades at once, it can work on all of them at the same time. This is for total efficiency, and it's easy to work with!

It's **event based**, so that means you won't have code, doing loops, polling for trades, we do all that for you. All you have to write is a listener `@manager.on('new_trade')` and your function to proccess the event.

## Installation
You'll need to install this through pip, Python's package manager. If you don't have pip installed, then you arn't using the lastest version of python needed to run this program.
```bash
pip install -U steam-trade
```
Then, you will access it under a diffrent name when importing it:
```py
from pytrade import *
```
