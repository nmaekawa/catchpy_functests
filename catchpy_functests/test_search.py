import json
import requests
import os
import pytest

from .utils import get_token
from .utils import has_tag
from .utils import find_reply_to
from .utils import find_media_type
from .utils import API_URL



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

    url = '{}/search?userid={}&userid={}'.format(
        API_URL, testvars['creator2'], testvars['creator3'])

    r = requests.get(url, headers=header)
    assert r.status_code == 200

    resp = json.loads(r.content)
    assert resp['total'] == 48
    assert resp['size'] == 10


@pytest.mark.usefixtures('testvars')
def test_username(testvars):
    token = get_token(user=testvars['creator3'], apikey=testvars['api_key'],
                      secretkey=testvars['secret_key'])
    header = {'Authorization': 'Token {}'.format(token),
              'Content-Type': 'application/json'}

    url = '{}/search?username=user_{}'.format(API_URL, testvars['creator3'])

    r = requests.get(url, headers=header)
    assert r.status_code == 200

    resp = json.loads(r.content)
    assert resp['total'] == 28
    assert resp['size'] == 10


@pytest.mark.usefixtures('testvars')
def test_tags(testvars):
    token = get_token(user=testvars['creator3'], apikey=testvars['api_key'],
                      secretkey=testvars['secret_key'])
    header = {'Authorization': 'Token {}'.format(token),
              'Content-Type': 'application/json'}

    url = '{}/search?tag={}&limit=-1'.format(API_URL, testvars['common_tag'])

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

    url = '{}/search?tag={}&userid={}'.format(
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

    url = '{}/search?media=Annotation&limit=-1'.format(API_URL)

    r = requests.get(url, headers=header)
    assert r.status_code == 200

    resp = json.loads(r.content)
    assert resp['total'] == 28


@pytest.mark.usefixture('testvars')
def test_anno_with_replies(testvars):
    token = get_token(user=testvars['creator3'], apikey=testvars['api_key'],
                      secretkey=testvars['secret_key'])
    header = {'Authorization': 'Token {}'.format(token),
              'Content-Type': 'application/json'}

    number_of_replies = 5
    index = 'reply_to_{}'.format(number_of_replies)
    url = '{}/search?sourceId={}&limit=-1'.format( API_URL, testvars[index])

    r = requests.get(url, headers=header)
    assert r.status_code == 200

    resp = json.loads(r.content)
    for x in resp['rows']:
        assert x['platform']['target_source_id'] == testvars[index]
    assert resp['total'] == number_of_replies


@pytest.mark.usefixtures('testvars')
def test_by_media_userid_contextid(testvars):
    token = get_token(user=testvars['creator3'], apikey=testvars['api_key'],
                      secretkey=testvars['secret_key'])
    header = {'Authorization': 'Token {}'.format(token),
              'Content-Type': 'application/json'}
    media = 'Video'
    userId = testvars['creator2']
    contextId = 'fake_context'
    url = '{}/search?media={}&userid={}&contextId={}'.format(
        API_URL, media, userId, contextId)
    r = requests.get(url, headers=header)
    assert r.status_code == 200

    resp = json.loads(r.content)
    assert resp['total'] == 5
    for x in resp['rows']:
        assert x['platform']['contextId'] == contextId
        assert x['creator']['id'] == userId
        assert find_media_type(x) == media

