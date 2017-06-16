from datetime import datetime
from dateutil import tz
import json
import requests
import os
import pytest

from .utils import get_token
from .utils import has_tag
from .utils import find_reply_to
from .utils import find_media_type
from .utils import API_URL
from .utils import make_encoded_token

# main idea:
# make each call to catch-dev and compare to a call to local catchpy


# create a bunch of anno
# they'll differ in id, and dates created/modified
# if reply: differ in reply_to (parent)

#
# payload = {
#   "consumerKey": "thisisafakeconsumerkey",
#    "userId": "user_x",
#    "issuedAt": "dateiniso8601format",
#    "ttl": "30secondstoexpire",
#    "override": ["CAN_READ", "CAN_UPDATE"]
# }

class CatchServer(object):

    def __init__(self, url, api_key, secret_key):
        self.url = url
        self.api_key = api_key
        self.secret_key

    def token(payload):
        ''' must have 'userId' and 'override' defined.'''

        payload['consumerKey'] = self.api_key
        payload['issuedAt'] = \
            datetime.now(tz=tz.tzutc).replace(microsecond=0).isoformat()
        if 'ttl' not in payload:
            payload['ttl'] = 60
        return make_encoded_token(
            secret=self.secret_key, payload=payload)


#def create(server, wa):

def test_1():
    x = make_encoded_token('123', {'blah': 'blog'})
    assert 1 > 0


