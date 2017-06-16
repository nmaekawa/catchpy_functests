import os

import os, sys

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_settings')

import django
django.setup()

import json
import os.path
from random import randint
import requests
from urllib.parse import urlparse
from uuid import uuid4

import time

from catchformats.catch_webannotation_validator import wa_are_similar

from anno.models import ANNO, AUDIO, IMAGE, TEXT, VIDEO, THUMB
from anno.tests.conftest import make_wa_object
from anno.tests.conftest import make_wa_tag
from anno.tests.conftest import make_jwt_payload
from anno.tests.conftest import make_encoded_token


class DataGeneratorForCatchpy(object):

    MEDIAS = [AUDIO, TEXT, VIDEO, IMAGE]

    def __init__(self, api_url, api_key, secret_key):
        self.api_url = api_url
        self.__api_key = api_key
        self.__secret_key = secret_key
        self._created = {}


    def get_token(self, user):
        payload = make_jwt_payload(apikey=self.__api_key,
                                   user=user)
        token = make_encoded_token(secret=self.__secret_key,
                                   payload=payload)
        return token


    def generate_set(self, size=1, user=None, media=TEXT, reply_to=None):
        wa_set = []
        for i in range(0, size):
            wa_set.append(make_wa_object(1, media, user=user, reply_to=reply_to))

        return wa_set


    def generate_set_assorted_media(self, size=1, user=None):
        wa_set = []
        for i in range(0, size):
            for media in DataGeneratorForCatchpy.MEDIAS:
                wa_set.append(make_wa_object(1, media, user=user))

        return wa_set


    def add_tag(self, wa_set, tagname):
        for wa in wa_set:
            wa['body']['items'].append(make_wa_tag(tagname))
        return wa_set


    def replace_target_source(self, wa_set, target_source):
        for wa in wa_set:
            wa['target']['items'][0]['source'] = target_source
        return wa_set


    def send_create(self, wa):
        '''send request to create wa.'''
        token = self.get_token(user=wa['creator']['id'])
        header = {'Authorization': 'Token {}'.format(token),
                  'Content-Type': 'application/json'}

        r = requests.post('{}/{}'.format(self.api_url, wa['id']),
                          headers=header,
                          data=json.dumps(wa),
                          allow_redirects=False)
        if r.status_code != 303:
            print(
                ('error in request to create wa; status_code({} '
                '- {}): {} ****************** {}').format(
                    r.status_code, r.reason, json.dumps(r.json()),
                    json.dumps(wa)),
                file=sys.stderr
            )
            return None
        else:
            # get id from just created annotation
            location = r.headers.get('location', None)
            if location:
                o = urlparse(location)
                wa_id = os.path.basename(o.path)
                wa = r.json()
                self._created[wa_id] = wa

                assert wa_id == wa['id']

                wa_resp = r.json()
                assert wa_are_similar(wa, wa_resp)

                return wa
            else:
                print('error in response to create: no Location header')
                return None


    def replace_body_text(self, wa_set, text):
        for wa in wa_set:
            for b in wa['body']['items']:
                if b['purpose'] == 'commenting':
                    b['value'] = text
                    break
        return wa_set


    def do_create_set(self, params):
        creator1 = params['creator1']
        creator2 = params['creator2']
        creator3 = params['creator3']
        common_tag = params['common_tag']
        common_target_source = params['common_target_source']
        common_body_text = params['common_body_text']

        # creator1 and creator2 have 1 annotation of each type
        set1 = []  # 4 annot each
        for creator in [creator1, creator2]:
            for media in DataGeneratorForCatchpy.MEDIAS:
                set1 += self.generate_set(size=1, user=creator, media=media)
        set2 = []
        for i in range(0, len(set1)):
            wa = set1[i]
            r = self.send_create(wa)
            set2 += self.generate_set(
                size=i, user=creator3, media=ANNO, reply_to=wa['id'])
            params['reply_to_{}'.format(i)] = wa['id']

        # creator3 send i replies to each of annotations above
        for wa in set2:  # 28 annot for creator3
            r = self.send_create(wa)

        # set with same tag
        set3 = []
        for creator in [creator1, creator2]:
            set3 += self.generate_set_assorted_media(size=2, user=creator)
        set3 = self.add_tag(set3, common_tag)
        for wa in set3:  # 8 each
            r = self.send_create(wa)

        # set with same target_source
        set4 = self.generate_set_assorted_media(size=2, user=creator1)
        set4 = self.replace_target_source(set4, common_target_source)
        for wa in set4:  # 8 for creator1
            r = self.send_create(wa)

        # set with same body_text
        set5 = self.generate_set_assorted_media(size=2, user=creator2)
        set5 = self.replace_body_text(set5, common_body_text)
        for wa in set5:  # 8 for creator2
            r = self.send_create(wa)


if __name__ == '__main__':
    params = {
        'creator1': str(uuid4()),
        'creator2': str(uuid4()),
        'creator3': str(uuid4()),
        'common_tag': 'supercalifragilisticexpialidocious',
        'common_target_source': 'http://hardwork.harvardx.harvard.edu',
        'common_body_text': ('strange women lying in ponds distributing swords '
                             'is no basis for a system of government'),
    }
    keys = {
        'api_url': 'http://localhost:8000/anno',
        'api_key': '5b16376c-0455-46c4-8780-bb016ef9e6fc',
        'secret_key': 'd64a565b-be9c-4659-9671-d30dcad9844a',
    }

    generator = DataGeneratorForCatchpy(**keys)
    generator.do_create_set(params)

    params.update(keys)
    print(json.dumps(params, sort_keys=True, indent=4))
    print('\nDONE!\n')








