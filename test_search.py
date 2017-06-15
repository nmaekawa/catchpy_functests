import os, sys

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_settings')

import django
django.setup()

import json
import jwt
import requests
import pytest

from anno.models import Anno, Tag, Target
from anno.models import PURPOSE_TAGGING
from anno.models import ANNO, AUDIO, IMAGE, TEXT, VIDEO, THUMB
from anno.tests.conftest import make_jwt_payload
from anno.tests.conftest import make_encoded_token

API_URL = 'http://localhost:8000/anno/search?'


def get_token(user, apikey, secretkey):
    payload = make_jwt_payload(apikey, user=user)
    token = make_encoded_token(secret=secretkey, payload=payload)
    return token


@pytest.fixture(scope='module')
def testvars():
    testvars_filename = '{}_main_vars.json'.format(os.environ.get('CATCH_DB', 'test'))
    testvars_path = os.path.join(os.getcwd(), testvars_filename)

    with open(testvars_path, 'r') as f:
        read_data = f.read()

    return json.loads(read_data)


@pytest.mark.usefixtures('testvars')
def test_userid(testvars):
    token = get_token(user=testvars['creator1'], apikey=testvars['api_key'],
                      secretkey=testvars['secret_key'])
    header = {'Authorization': 'Token {}'.format(token),
              'Content-Type': 'application/json'}

    url = '{}userid={}&userid={}'.format(API_URL,
                                         testvars['creator2'],
                                         testvars['creator3']
                                        )

    r = requests.get(url, headers=header)
    assert r.status_code == 200

    resp = json.loads(r.content)
    assert resp['total'] == (28 + 12)
    assert resp['size'] == 10


@pytest.mark.usefixtures('testvars')
def test_username(testvars):
    token = get_token(user=testvars['creator3'], apikey=testvars['api_key'],
                      secretkey=testvars['secret_key'])
    header = {'Authorization': 'Token {}'.format(token),
              'Content-Type': 'application/json'}

    url = '{}username=user_{}'.format(API_URL, testvars['creator3'])

    r = requests.get(url, headers=header)
    assert r.status_code == 200

    resp = json.loads(r.content)
    assert resp['total'] == 12
    assert resp['size'] == 10


@pytest.mark.usefixtures('testvars')
def test_tags(testvars):
    token = get_token(user=testvars['creator3'], apikey=testvars['api_key'],
                      secretkey=testvars['secret_key'])
    header = {'Authorization': 'Token {}'.format(token),
              'Content-Type': 'application/json'}

    url = '{}tag={}&limit=-1'.format(API_URL, testvars['common_tag'])

    r = requests.get(url, headers=header)
    assert r.status_code == 200

    resp = json.loads(r.content)
    assert resp['total'] == 16

    # check only creator1 and 2 are in response
    count = [0, 0, 0]
    for x in resp['rows']:
        assert has_tag(x, testvars['common_tag'])

        if x['creator']['id'] == testvars['creator1']:
            count[0] += 1
        elif x['creator']['id'] == testvars['creator2']:
            count[1] += 1
        elif x['creator']['id'] == testvars['creator3']:
            count[2] += 1
    assert count[0] == 8
    assert count[1] == 8
    assert count[2] == 0

    url = '{}tag={}&userid={}'.format(
        API_URL, testvars['common_tag'], testvars['creator2'])
    r = requests.get(url, headers=header)
    assert r.status_code == 200
    resp = json.loads(r.content)
    assert resp['total'] == 8
    for x in resp['rows']:
        assert has_tag(x, testvars['common_tag'])
        assert x['creator']['id'] == testvars['creator2']


@pytest.mark.usefixture('testvars')
def test_replies(testvars):
    token = get_token(user=testvars['creator3'], apikey=testvars['api_key'],
                      secretkey=testvars['secret_key'])
    header = {'Authorization': 'Token {}'.format(token),
              'Content-Type': 'application/json'}

    url = '{}media=Annotation&limit=-1'.format(API_URL)

    r = requests.get(url, headers=header)
    assert r.status_code == 200

    resp = json.loads(r.content)
    assert resp['total'] == 12


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

