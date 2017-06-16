import os, sys

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_settings')

import django
django.setup()

from anno.models import Anno, Tag, Target
from anno.models import PURPOSE_TAGGING
from anno.models import ANNO, AUDIO, IMAGE, TEXT, VIDEO, THUMB
from anno.tests.conftest import make_jwt_payload
from anno.tests.conftest import make_encoded_token


def get_token(user, apikey, secretkey):
    payload = make_jwt_payload(apikey, user=user)
    token = make_encoded_token(secret=secretkey, payload=payload)
    return token


#
# TODO: figure a way to gather utilities to deal with wa json
# without requiring to include django ORM definitions everywhere
# ex: PURPOSE_TAGGING
#
def has_tag(wa, tagname):
    for b in wa['body']['items']:
        if b['purpose'] == PURPOSE_TAGGING:
            if b['value'] == tagname:
                return True
    return False


def find_reply_to(wa):
    for t in wa['target']['items']:
        if t['type'] == ANNO:
            return t['source']
    return None

def find_media_type(wa):
    media_type = wa['target']['items'][0]['type']
    return IMAGE if media_type == THUMB else media_type

