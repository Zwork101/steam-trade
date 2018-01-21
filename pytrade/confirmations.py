import aiohttp
import asyncio
import base64
from bs4 import BeautifulSoup
from hashlib import sha1
import hmac
import time
import struct
from urllib.parse import urlencode


class Conf:
    def __init__(self, id, data_confid, data_key, manager, creator):
        self.id = id.split('conf')[1]
        self.data_confid = data_confid
        self.data_key = data_key
        self.tag = 'details' + self.id
        self.manager = manager
        self.creator = creator

    def _confirm_params(self, tag):
        timestamp = int(time.time())
        conf_key = self.manager.gen_conf_key(tag, timestamp)
        return {'p': self.manager.device_id,
                'a': self.manager.id,
                'k': conf_key.decode(),
                't': timestamp,
                'm': 'android',
                'tag': tag}

    async def confirm(self, loop=0):
        params = self._confirm_params('allow')
        params['op'] = 'allow'
        params['cid'] = self.data_confid
        params['ck'] = self.data_key
        try:
            async with self.manager.session.get(self.manager.CONF_URL + '/ajaxop', params=params) as resp:
                 r = resp.text()
                 return (True, r)
        except TypeError:
            if loop:
                return (False, "Unable to re-login")
            self.manager.logged_on = False
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.ensure_future(self.manager.login()))
            await self.confirm(loop=1)

    async def anfirm(self):
        params = self._confirm_params('cancel')
        params['op'] = 'cancel'
        params['cid'] = self.data_confid
        params['ck'] = self.data_key
        async with self.manager.session.get(self.manager.CONF_URL + '/ajaxop', params=params) as resp:
            r = await resp.text()
            return (True, r)

    async def details(self):
        params = self._confirm_params(self.tag)
        async with self.manager.session.get(ConfManager.CONF_URL + '/details/' + self.id,
                                            params=params) as resp:
            d = await resp.json()['html']
            return (True, d)


class ConfManager:
    CONF_URL = "https://steamcommunity.com/mobileconf"

    def __init__(self, identity_secret: str, steamid: str, session: aiohttp.ClientSession):
        self.id_secret = identity_secret
        self.id = steamid
        self.session = session

    def gen_conf_key(self, tag: str, timestamp: int = None):
        if not timestamp:
            timestamp = int(time.time())
        buff = struct.pack('>Q', timestamp) + tag.encode('ascii')
        return base64.b64encode(hmac.new(base64.b64decode(self.id_secret), buff, digestmod=sha1).digest())

    def _create_confirmation_params(self, tag):
        timestamp = int(time.time())
        confirmation_key = self.gen_conf_key(tag)
        return {'p': self.device_id,
                'a': self.id,
                'k': confirmation_key.decode(),
                't': timestamp,
                'm': 'android',
                'tag': tag}

    async def get_confirmations(self):
        confs = ''
        params = self._create_confirmation_params('conf')
        headers = {'X-Requested-With': 'com.valvesoftware.android.steam.community'}
        
        try:
            async with self.session.get(self.CONF_URL + '/conf?' + urlencode(params), headers=headers) as resp:
                txt = await resp.text()
                if 'incorrect Steam Guard codes.' in txt:
                    return (False, txt)
                confs = txt
                if 'Oh nooooooes!' in txt:
                    return (False, txt)
        except ValueError:
            await self.login(self.async_client)
            async with self.session.get(self.CONF_URL + '/conf?' + urlencode(params), headers=headers) as resp:
                txt = await resp.text()
                if 'incorrect Steam Guard codes.' in txt:
                    return (False, txt)
                confs = txt
                if 'Oh nooooooes!' in txt:
                    return (False, txt)
            
        soup = BeautifulSoup(confs, 'html.parser')
        if soup.select('#mobileconf_empty'):
            return (True, [])
        confirms = []
        for confirmation in soup.select('#mobileconf_list .mobileconf_list_entry'):
            id = confirmation['id']
            confid = confirmation['data-confid']
            key = confirmation['data-key']
            creator = confirmation.get('data-creator')
            confirms.append(Conf(id, confid, key, self, creator))
        return (True, confirms)

    async def get_trade_confirmation(self, trade_offer_id, confs=None):
        if confs is None:
            confs = await self.get_confirmations()
            if not confs[0]:
                return (False, confs[1])
            confs = confs[1]
        for conf in confs:
            if conf.creator == trade_offer_id:
                return (True, conf)
        return (False, f"Could not find confirmation for trade: {trade_offer_id}")

    @property
    def device_id(self):
        hexed_steam_id = sha1(self.id.encode('ascii')).hexdigest()
        return 'android:' + '-'.join([hexed_steam_id[:8],
                                      hexed_steam_id[8:12],
                                      hexed_steam_id[12:16],
                                      hexed_steam_id[16:20],
                                      hexed_steam_id[20:32]])
