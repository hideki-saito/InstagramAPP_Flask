import requests
import random
from random import randint
import hmac
import hashlib
import uuid
import json
import time
import urllib.parse

VERSIONS = ('GT-N7000', 'SM-N9000', 'GT-I9220', 'GT-I9100')
RESOLUTIONS = ('720x1280', '320x480', '480x800', '1024x768', '1280x720', '768x1024', '480x320')
DPIS = ('120', '160', '320', '240')


def generate_user_agent():
    ver = random.choice(VERSIONS)
    res = random.choice(RESOLUTIONS)
    dpi = random.choice(DPIS)

    inst_version = '9.0.1'
    and_version = str(randint(10, 11)) + '/' + '.'.join([str(p) for p in [randint(1, 3), randint(3, 5), randint(0, 5)]])

    return 'Instagram %s Android (%s; %s; %s; samsung; %s; %s; smdkc210; en_US)' % \
           (inst_version, and_version, dpi, res, ver, ver)


def generate_signature(data):
    return hmac.new(
        '96724bcbd4fb3e608074e185f2d4f119156fcca061692a4a1db1c7bf142d3e22'.encode('utf-8'),
        data.encode('utf-8'), hashlib.sha256).hexdigest()


class PynstagramSession(object):
    ENDPOINT_URL = 'https://i.instagram.com/api/v1'

    def __init__(self):
        self.guid = str(uuid.uuid1())
        self.device_id = 'android-4bca48fddbe5477d'
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': generate_user_agent()})

    def login(self, username, password):
        data = json.dumps({
            'device_id': self.device_id,
            '_uuid': self.guid,
            'username': username,
            'password': password,
            '_csrftoken': 'missing',
            'login_attempt_count': 0
        })

        sig = generate_signature(data)

        payload = 'signed_body=%s.%s&ig_sig_key_version=4' % (sig, data)
        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        resp = self.session.post(self.ENDPOINT_URL + '/accounts/login/', payload, headers=headers)
        resp_json = resp.json()

        if resp_json.get('status') != 'ok':
            raise IOError(resp_json.get('message'))

    def upload_photo(self, path):
        data = {
            '_csrftoken': 'missing',
            'upload_id': int(time.time()),
            'device_id': self.device_id,
            '_uuid': self.guid,
            'image_compression': '{"lib_name":"jt","lib_version":"1.3.0","quality":"70"}',
            'filename': 'pending_media_{}.jpg'.format(time.time())
        }
        files = {'photo': open(path, 'rb')}

        resp = self.session.post(self.ENDPOINT_URL + '/upload/photo/', data, files=files)
        resp_json = resp.json()

        media_id = resp_json.get('upload_id')
        if media_id is None:
            raise IOError(resp_json.get('message'))
        return media_id

    def configure_photo(self, media_id, caption):
        data = json.dumps({
            'device_id': self.device_id,
            '_uuid': self.guid,
            '_csrftoken': 'missing',
            'media_id': media_id,
            'caption': caption,
            'device_timestamp': time.time(),
            'source_type': "5",
            'filter_type': "0",
            'extra': '{}',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        })

        sig = generate_signature(data)

        payload = 'signed_body={}.{}&ig_sig_key_version=4'.format(
            sig,
            urllib.parse.quote(data))

        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        resp = self.session.post(self.ENDPOINT_URL + '/media/configure/', payload, headers=headers)
        resp_json = resp.json()

        if resp_json.get('status') != 'ok':
            raise IOError(resp_json.get('message'))
