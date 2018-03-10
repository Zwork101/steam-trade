import asyncio
from pyee import EventEmitter
from pytrade import confirmations, EconItem, EconTradeOffer, login, manager_trade, steam_enums


class GlobalManager(EventEmitter):
    def __init__(self, modules: list, poll_delay: int=2):
        """
        :param modules: modules to poll
        :param poll_delay: how long to wait after polling finishes until polling starts again
        """
        self.modules = modules
        self.poll_delay = poll_delay
        EventEmitter.__init__(self)

    async def _run_forever(self):
        while True:
            self.emit('global_start_poll')
            for zwork in self.modules:
                await zwork.poll()
            self.emit('global_end_poll')
            await asyncio.sleep(self.poll_delay)

    def run_forever(self):
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(self._run_forever())
        loop.run_forever()
