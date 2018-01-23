from steamid import SteamID
from pytrade.steam_enums import ETradeOfferState, SteamUrls
from pytrade.EconItem import Item
import asyncio
import json


def get_ids(item: Item):
    return {'assetid': item.assetid, 'classid': item.classid, 'instanceid': item.instanceid, 'amount': item.amount}


def merge_item(ids, desc):
    for key, value in ids.items():
        desc[key] = value
    return desc


def require_manager_key(func):
    async def wrapper(*args, **kwargs):
        if args[0].manager is None:
            raise ValueError("Manager is required")
        if args[0].manager.key is None:
            raise ValueError("Key not found")
        return await func(*args, **kwargs)

    return wrapper


class TradeOffer:
    def __init__(self, data, descriptions=None, manager=None, parse_items=True):
        if descriptions is None:
            descriptions = []
        self._load(data, descriptions, manager, parse_items)

    def _load(self, data, desc, manager, parse_items):
        # Define basic variables, set attributes
        self.raw = data
        self.raw_descriptions = desc
        self.manager = manager
        self.tradeofferid = data.get('tradeofferid', '')
        self.steamid_other = SteamID(str(data.get('accountid_other', 309304171) + 76561197960265728))
        self.message = data.get('message')
        self.expiration_time = data.get('expiration_time')
        self.is_our_offer = data.get('is_our_offer')
        self.from_real_time_trade = data.get('from_real_time_trade')
        self.escrow_end_date = data.get('escrow_end_date')
        self.items_to_give = []
        self.items_to_receive = []
        self._counter = 0
        self._sent = True if self.tradeofferid else False

        # Check each enum for the one equal to the state. Should it raise an error, if the status isn't valid?
        for enum in ETradeOfferState:
            if enum.value == data.get('trade_offer_state', 1):
                self.trade_offer_state = enum

        # If it shouldn't parse the items, just set them.
        # REMEMBER: if you choose to have items pre-parsed, it will assume you supplied both attributes
        if not parse_items:
            self.items_to_give = data['items_to_give']
            self.items_to_receive = data['items_to_receive']
            return

        # For each item in the items we're giving, check it
        for item in data.get('items_to_give', []):
            if not item.get('missing', False):  # If missing, it's not in the trade
                for description in desc:  # For each description in descriptions, check to see it matches item
                    desc_id = description['classid'] + '_' + description['instanceid']
                    if desc_id == item['classid'] + '_' + item['instanceid']:
                        self.items_to_give.append(Item(merge_item(item, description)))  # If so, parse and append
                        break
            else:
                self.items_to_give.append(Item(item, True))  # If it's missing, just add the item ids as an Item

        for item in data.get('items_to_receive', []):
            if not item.get('missing', False):
                for description in desc:
                    desc_id = description['classid'] + '_' + description['instanceid']
                    if desc_id == item['classid'] + '_' + item['instanceid']:
                        self.items_to_receive.append(Item(merge_item(item, description)))
                        break
            else:
                self.items_to_receive.append(Item(item, True))

    @require_manager_key
    async def update(self):
        this_offer = await self.manager.api_call('GET', 'IEconService', 'GetTradeOffer', 'v1', key=self.manager.key,
                                                 tradeofferid=self.tradeofferid, language=self.manager.language)
        if not this_offer[0]:
            return False, this_offer[1]
        this_offer = this_offer[1]
        self._load(this_offer['response']['offer'], this_offer['response'].get('descriptions', []), self.manager, True)
        return True, self

    @require_manager_key
    async def cancel(self):
        if self.trade_offer_state != ETradeOfferState.Active and \
                        self.trade_offer_state != ETradeOfferState.CreatedNeedsConfirmation:
            return False, 'This trade is not active'
        elif not self.is_our_offer:
            return False, "This is not our trade, try declining."
        return await self.manager.api_call('POST', 'IEconService', 'CancelTradeOffer', 'v1',
                                           key=self.manager.key, tradeofferid=self.tradeofferid)


    @require_manager_key
    async def decline(self):
        if self.trade_offer_state != ETradeOfferState.Active and \
                        self.trade_offer_state != ETradeOfferState.CreatedNeedsConfirmation:
            return False, 'This trade is not active'
        elif self.is_our_offer:
            return False, "This is our trade, try canceling."
        return await self.manager.api_call('POST', 'IEconService', 'DeclineTradeOffer', 'v1',
                                           key=self.manager.key, tradeofferid=self.tradeofferid)

    @require_manager_key
    async def accept(self, token=''):
        if self.trade_offer_state != ETradeOfferState.Active:
            return False, "This trade is not active. If you think it is, try updating it"
        session_cookie = self.manager.get_session()
        url = SteamUrls.Community.value + '/tradeoffer/' + self.tradeofferid + '/accept'
        info = {'sessionid': session_cookie,
                'tradeofferid': self.tradeofferid,
                'serverid': 1,
                'partner': self.steamid_other.toString(),
                'captcha': ''
                }
        headers = {'Referer': f"https://steamcommunity.com/tradeoffer/{self.tradeofferid}/"}
        async with self.manager.session.post(url, data=info, headers=headers) as resp:
            resp_json = await resp.json()
            if resp_json.get('needs_mobile_confirmation', False):
                if self.manager.id_secret:
                    await asyncio.sleep(2)
                    tries = 1
                    while tries <= 3:
                            conf = await self.manager.get_trade_confirmation(self.tradeofferid)
                            if not conf[0]:
                                tries += 1
                                continue
                            conf = conf[1]
                            resp = await conf.confirm()
                            if resp[0]:
                                 return True, conf
                            return False, resp[1]
                    return False, "Couldn't find confirmation"
            return True, resp_json

    @require_manager_key
    async def ship(self, counter='', token=''):
        if not self._sent:
            return False, "Trade already shipped"

        if not self.items_to_receive and not self.items_to_give:
            return False, "Can't have trade with 0 items"

        our_offer = {
            "newversion": True,
            "version": 4,
            "me": {
                "assets": list(map(get_ids, self.items_to_give)),
                "currency": [],
                "ready": False
            },
            "them": {
                "assets": list(map(get_ids, self.items_to_receive)),
                "currency": [],
                "ready": False
            }}

        trade_prams = '{}'
        if token:
            trade_prams = {'trade_offer_access_token':token}
            trade_prams = json.dumps(trade_prams)

        data = {
            'sessionid': self.manager.get_session(),
            'serverid': 1,
            'partner': self.steamid_other.toString(),
            'tradeoffermessage': self.message[:128],
            'json_tradeoffer': json.dumps(our_offer),
            'captcha': '',
            'trade_offer_create_params': trade_prams
        }
        headers = {'Referer': SteamUrls.Community.value + '/tradeoffer/new/?partner=' + self.steamid_other.accountid,
                   'Origin': SteamUrls.Community.value}
        async with self.manager.session.post(SteamUrls.Community.value + '/tradeoffer/new/send',
                                             data=data, headers=headers):
            pass
