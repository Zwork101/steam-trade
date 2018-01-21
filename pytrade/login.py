from pytrade.steam_enums import SteamUrls
import aiohttp
import rsa
import base64
import struct
import hmac
from hashlib import sha1
import time
from yarl import URL

class AsyncClient:

    def __init__(self, username, password, shared_secret=None, one_time_code=''):
        self.username = username
        self.password = password
        self.shared_secret = shared_secret
        self.session = aiohttp.ClientSession()
        self._repeats = 0
        self._one_time_code = one_time_code
        self.logged_in = False

    async def test_login(self):
        async with self.session.get(SteamUrls.Community.value) as resp:
           # print(await resp.text())
            if self.username in await resp.text():
                self.logged_in = True
                return True
        return False

    async def do_login(self):
        login_request = await self._send_login()
        if 'captcha_needed' in login_request.keys():
            raise ValueError("Captcha required for login")

        if not login_request['success']:
            raise ValueError(f"Invalid Credentials: {login_request.get('message')}")

        await self._do_redirect(login_request)
        community_domain = SteamUrls.Community.value[8:]
        store_domain = SteamUrls.Store.value[8:]
        new_cookies = self._copy_cookies(store_domain, community_domain)
        self.session.cookie_jar.update_cookies(new_cookies, URL(SteamUrls.Community.value))
        if not await self.test_login():
            self.logged_in = False
            raise ConnectionError('Login Failed')
        self.logged_in = True
        return self.session

    def _copy_cookies(self, prev_domain, new_domain):
        prev_cookies = self.session.cookie_jar.filter_cookies(prev_domain)
        for cookie in prev_cookies:
            cookie['domain'] = new_domain
        return prev_cookies

    async def _get_rsa(self):
        async with self.session.post(SteamUrls.Store.value + '/login/getrsakey/',
                                     data={'username': self.username}) as resp:
            resp = await resp.json()
            try:
                mod = int(resp['publickey_mod'], 16)
                exp = int(resp['publickey_exp'], 16)
                timestamp = resp['timestamp']
            except KeyError:
                if self._repeats >= 10:
                    raise ValueError("Unable to obtain rsa keys")
                else:
                    self._repeats += 1
                    return await self._get_rsa()
            else:
                return {'rsa_key': rsa.PublicKey(mod, exp), 'rsa_timestamp': timestamp}

    async def _send_login(self):
        try:
            rsa_keys = await self._get_rsa()
        except aiohttp.client_exceptions.ClientConnectorError:
            rsa_keys = await self._get_rsa()
        encrypt_pass = self._encrypt_password(rsa_keys)
        request_payload = self._prep_login(encrypt_pass, rsa_keys['rsa_timestamp'])
        async with self.session.post(SteamUrls.Store.value + '/login/dologin', data=request_payload) as resp:
            return await resp.json()

    def _encrypt_password(self, rsa_params: dict):
        return base64.b64encode(rsa.encrypt(self.password.encode('utf-8'), rsa_params['rsa_key']))

    def _prep_login(self, encrypt_pass: bytes, timestamp: str):
        return {
            'password': encrypt_pass.decode(),
            'username': self.username,
            'twofactorcode': self.one_time_code,
            'emailauth': '',
            'loginfriendlyname': '',
            'captchagid': '-1',
            'captcha_text': '',
            'emailsteamid': '',
            'rsatimestamp': timestamp,
            'remember_login': 'false',
            'donotcache': str(int(time.time() * 1000))
        }

    async def _do_redirect(self, resp_json):
        prams = resp_json.get('transfer_parameters')
        if not prams:
            raise Exception('transfer_parameters not found. Steam is having issues')
        for url in resp_json['transfer_urls']:
            async with self.session.post(url, data=prams) as resp:
                pass

    @property
    def one_time_code(self):
        if self._one_time_code:
            return self._one_time_code
        elif not self.shared_secret:
            return input("Please enter one time code: ")
        #This code can be found in the steampy modual. I'm not smart enough to understand this.
        time_buffer = struct.pack('>Q', int(time.time()) // 30)  # pack as Big endian, uint64
        time_hmac = hmac.new(base64.b64decode(self.shared_secret), time_buffer, digestmod=sha1).digest()
        begin = ord(time_hmac[19:20]) & 0xf
        full_code = struct.unpack('>I', time_hmac[begin:begin + 4])[0] & 0x7fffffff  # unpack as Big endian uint32
        chars = '23456789BCDFGHJKMNPQRTVWXY'
        code = ''

        for _ in range(5):
            full_code, i = divmod(full_code, len(chars))
            code += chars[i]

        return code
