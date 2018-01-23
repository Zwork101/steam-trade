from pytrade.steam_enums import SteamUrls, ETradeOfferState
from pytrade.EconTradeOffer import TradeOffer, merge_item
from pytrade.EconItem import Item
from pytrade.confirmations import ConfManager
from steamid import SteamID
import aiohttp
import asyncio
from pyee import EventEmitter
import re
from copy import copy

def require_login(func):
    async def wrapper(*args, **kwargs):
        if not args[0].logged_in:
            raise ValueError("Manager is not logged in")
        return await func(*args, **kwargs)
    return wrapper

def require_key(func):
    async def wrapper(*args, **kwargs):
        if not args[0].key:
            raise ValueError("Could not find key")
        return await func(*args, **kwargs)
    return wrapper

class TradeManager(EventEmitter, ConfManager):

    """
    This is the TradeManager object, it inherits from the ConfManager and EventEmitter objects.
    """

    def __init__(self, steamid, key=None, language='en', identity_secret='', poll_delay=30):
        EventEmitter.__init__(self)
        self.session = aiohttp.ClientSession()
        ConfManager.__init__(self, identity_secret, steamid, self.session)
        self.steamid = SteamID(steamid)
        if not self.steamid.isValid() or not self.steamid.type == SteamID.Type['INDIVIDUAL']:
            raise ValueError(f"Steam ID {self.steamid} is not valid, or is not a user ID")
        self.key = key
        self.language = language
        self.poll_delay = poll_delay
        self.logged_in = False
        self._trade_cache = {}
        self._conf_cache = {}
        self.first_run = True

    async def login(self, async_client):
        """
        Take a AsyncClient object, using the do_login method is optional.
        You must have passed in all credentials and requirements to the client already.
        Please make sure to run this first, just like in the example.py

        :param async_client: Does not need to be logged in, import from pytrade.login
        """
        if self.first_run:
            self.async_client = copy(async_client)
            self.first_run = False
        
        if async_client.logged_in:
            self.session = async_client.session
            self.logged_in = True
        else:
            session = await async_client.do_login()
            if await async_client.test_login():
                self.session = session
                self.logged_in = True
            else:
                raise ValueError("Login Failed")
        self.emit('logged_on')

    async def _run_forever(self):
        while True:
            self.emit('start_poll')
            #Check for current actions, then parse them
            await self._trade_poll()
            await self._confirmation_poll()
            self.emit('end_poll')
            await asyncio.sleep(self.poll_delay)

    def run_forever(self):
        """
        Run the bot forever, unless the time sense calling the function is greater than timeout.

        :param timeout: :class int/float:
        :return: (Will never return, but if it does, None)
        """
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(self._run_forever())
        loop.run_forever()

    @require_key
    async def get_trade_offers(self, active_only=True, sent=False, received=True):
        """
        get your trade offers, key is required.

        :param active_only:
        :`param sent:
        :param received:
        :return trade_list:
        """
        
        try:
            offers = await self.api_call('GET', 'IEconService', 'GetTradeOffers', 'v1', langauge=self.language,
                            get_descriptions=1, active_only=1, get_sent_offers=1, get_received_offers=1, key=self.key)
        except (ValueError, aiohttp.client_exceptions.ClientOSError, aiohttp.client_exceptions.ServerDisconnectedError):
            # aiohttp.client_exceptions.ClientOSError - [WinError 10054] An existing connection was forcibly closed by the remote host
            await self.login(self.async_client)
            offers = await self.api_call('GET', 'IEconService', 'GetTradeOffers', 'v1', langauge=self.language,
                        get_descriptions=1, active_only=1, get_sent_offers=1, get_received_offers=1, key=self.key)
        
        if offers[0]:
            offers = offers[1]
        else:
            return False, offers[1]
        
        sent_offers = []
        got_offers = []
        trade_offers = {}

        if sent:
            for offer in offers['response'].get('trade_offers_sent', []):
                trade_offer = TradeOffer(offer, offers['response'].get('descriptions', []), self)
                if trade_offer.trade_offer_state != ETradeOfferState.Active and active_only:
                    continue
                sent_offers.append(trade_offer)
            trade_offers['sent'] = sent_offers

        if received:
            for offer in offers['response'].get('trade_offers_received', []):
                trade_offer = TradeOffer(offer, offers['response'].get('descriptions', []), self)
                if trade_offer.trade_offer_state != ETradeOfferState.Active and active_only:
                    continue
                got_offers.append(trade_offer)
            trade_offers['received'] = got_offers

        return True, trade_offers

    async def _trade_poll(self):
        #First, check for new trades
        
        trades = await self.get_trade_offers(True, True, True)
        
        if not trades[0]:
            self.emit('poll_error', trades[1])
            return
        
        trades = trades[1]
        got_trades = trades.get('received', [])
        sent_trades = trades.get('sent', [])
        
        for trade in got_trades:
            if trade.tradeofferid not in self._trade_cache.keys():
                self._trade_cache[trade.tradeofferid] = trade
                if trade.trade_offer_state == ETradeOfferState.Active:
                    self.emit('new_trade', trade)
            else:
                self._test_states(trade)
        for trade in sent_trades:
            if trade.tradeofferid not in self._trade_cache.keys():
                self._trade_cache[trade.tradeofferid] = trade
                self.emit('trade_sent', trade)
            else:
                self._test_states(trade)

    async def _confirmation_poll(self):
        confs = await self.get_confirmations()
        
        if not confs[0]:
            self.emit('poll_error', confs[1])
            return
            
        for conf in confs[1]:
            if conf.id not in self._conf_cache.keys():
                self._conf_cache[conf.id] = conf
                self.emit('new_conf', conf)


    def _test_states(self, trade):
        if trade.trade_offer_state != self._trade_cache[trade.tradeofferid].trade_offer_state:
            self._trade_cache[trade.tradeofferid] = trade
            if trade.trade_offer_state == ETradeOfferState.Accepted:
                self.emit('trade_accepted', trade)
            elif trade.trade_offer_state == ETradeOfferState.Canceled:
                self.emit('trade_canceled', trade)
            elif trade.trade_offer_state == ETradeOfferState.Declined:
                self.emit('trade_declined', trade)
            elif trade.trade_offer_state == ETradeOfferState.Expired:
                self.emit('trade_expired', trade)
            elif trade.trade_offer_state == ETradeOfferState.Countered:
                self.emit('trade_countered', trade)
            else:
                self.emit('trade_state_changed', trade)


    async def api_call(self, method, api, call, version, **data):
        """
        Request data from steam through this function when using the API
        :param method:
        :param api:
        :param call:
        :param version:
        :kwargs data:
        :return json:
        """
        new_url = SteamUrls.Api.value + '/'.join(['', api, call, version])
        try:
            if method.lower() == 'get':
                async with self.session.get(new_url, params=data) as resp:
                    j = await resp.json()
                    return True, j
            elif method.lower() == 'post':
                async with self.session.post(new_url, data=data) as resp:
                    j = await resp.json()
                    return True, j
            elif method.lower() == 'delete':
                async with self.session.delete(new_url, data=data) as resp:
                    j = await resp.json()
                    return True, j
            elif method.lower() == 'put':
                async with self.session.put(new_url, data=data) as resp:
                    j = await resp.json()
                    return True, j
            else:
                raise ValueError(f"Invalid method: {method}")
        except aiohttp.ContentTypeError:
            html = await resp.text()
            return False, html

    def get_session(self):
        return self.session.cookie_jar._cookies['steamcommunity.com']['sessionid'].value

    def parse_token_from_url(self, trade_offer_url: str):
        reg = re.compile("https?:\/\/(www.)?steamcommunity.com\/tradeoffer\/new\/?\?partner=\d+(&|&amp;)token=(?P<token>[a-zA-Z0-9-_]+)")
        match = reg.match(trade_offer_url)
        if not match:
            return False, match
        return True, match['token']

    async def get_inventory(self, steamid: SteamID, appid, contextid=2, tradable_only=1):
        """
        Get a user's inventory

        :param steamid:
        :param appid:
        :param contextid:
        :param tradable_only:
        :return:
        """
        async with self.session.get(
            f"https://steamcommunity.com/profiles/{steamid.toString()}/inventory/json/{appid}/{contextid}",
            params = {'trading':tradable_only},
            headers = {"Referer": f"https://steamcommunity.com/profiles/{steamid.toString()}/inventory"}) as resp:
                inv = await resp.json()

        if not inv['success']:
            return False, inv

        items = []
        for _, item_id in inv['rgInventory'].items():
            id = item_id['classid'] + '_' + item_id['instanceid']
            item_desc = inv['rgDescriptions'].get(id)
            if item_desc is None:
                items.append(Item(item_id, True))
            items.append(Item(merge_item(item_id, item_desc)))
        return True, items

