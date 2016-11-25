import json
import re
import requests

from src.scripts.constants import *
from src.scripts.utils.IOutils import set_file_directory


LOCAL_ROOT = 'http://127.0.0.1:8000/api/v1'
LOCAL_HEADER = {'Authorization': 'token fc30ff32d078e97190558b7fdaf68fb392cec32d'}

ROOT = 'https://golewismcchord.herokuapp.com/api/v1'
HEADER = {'Authorization': 'token a3ef1e8d6724c13e58f86bc21261e8c7847d56dc'}

WIMM_ROOT = 'https://system.boomerangbike.com/api/v1/lewis_mcchord'
WIMM_HEADER = {'Authorization': 'token 015a10a2bb5a4c483b97137d30ddfb4e',
               'password': 'jblm'}


class DataRequest(object):

    objects = {}
    data_path = DATA_PATH

    def __init__(self, name, json_file, use_data_path=True):
        self.name = name

        if use_data_path and DataRequest.data_path:
            json_file = '{}{}'.format(DataRequest.data_path, json_file)
        set_file_directory(json_file)
        self.json_file = json_file
        self.data = None
        DataRequest.objects[name] = self

    def load_data(self):
        with open(self.json_file, 'r') as infile:
            return json.load(infile)

    def print_res(self, res, obj=None):
        if (re.search('4\d\d', str(res.status_code)) and not re.search('already exists', str(res.json())) and
                not re.search('unique set', str(res.json()))):
            print(self.name, res.json(), obj)

    def get(self):
        data = []
        # Get the entry list to all results
        res = requests.get('{}/{}/'.format(ROOT, self.name), headers=HEADER)
        # Copy results from each page to data
        while res:
            data += res.json()['results']
            done = None
            while not done:
                try:
                    res = requests.get(res.json()['next'], headers=HEADER) if res.json()['next'] else None
                    done = True
                except:
                    print('Get request had an interruption but is continuing.')

        # Export data to json_file
        with open(self.json_file, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)
        return True

    def post(self):
        if not self.data:
            self.data = self.load_data()
        for item in self.data:
            try:
                res = requests.post('{}/{}/'.format(ROOT, self.name), data=item, headers=HEADER)
            except:
                answer = None
                while not answer:
                    answer = input('Server connection has been interrupted. Reset dynos. (Press anything)')
                res = requests.post('{}/{}/'.format(ROOT, self.name), data=item, headers=HEADER)
            self.print_res(res, item)
        print('Post for {} complete'.format(self.name))

    def delete(self):
        res = requests.get('{}/{}/'.format(ROOT, self.name), headers=HEADER)
        while res.json()['results']:
            for item in res.json()['results']:
                requests.delete('{}/{}/{}/'.format(ROOT, self.name, item['id']), headers=HEADER)
            res = requests.get('{}/{}/'.format(ROOT, self.name), headers=HEADER)

    def post_user(self):
        if not self.data:
            self.data = self.load_data()

        # For each user
        for user in self.data:

            # Set the user
            user_json = {
                'username': user['id'],
                'password': user['last_name'].lower(),
                'email': user['id'],
                'groups': [int(i) for i in user['groups']],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'is_active': user['is_active'],
                'is_staff': user['is_staff']
            }
            res = requests.post('{}/user/'.format(ROOT), data=user_json, headers=HEADER)
            self.print_res(res, user_json)

        # After all users have been loaded set their end_user id
        res = requests.get('{}/user/'.format(ROOT), headers=HEADER)
        while res:
            for item in res.json()['results']:
                user = requests.get('{}/user/{}'.format(ROOT, item['id']), headers=HEADER).json()

                # Set user portion of the attributes
                end_res = requests.post('{}/end_user/'.format(ROOT), data={'id': user['username'],
                                                                           'user': user['id']}, headers=HEADER)
                self.print_res(end_res, user['username'])

            res = requests.get(res.json()['next'], headers=HEADER) if res.json()['next'] else None

        return True


def bulk_post():
    # First load
    DataRequest('agency', '/agency/agency.json').post()
    DataRequest('fleet', '/fleet/fleet.json').post()
    DataRequest('holiday', '/route/holiday.json').post()
    DataRequest('geography', '/stop/geography.json').post()
    # !DataRequest('group', '/user/group.json').post()!
    DataRequest('route', '/route/route.json').post()
    DataRequest('service', '/route/service.json').post()
    DataRequest('vehicle', '/vehicle/vehicle.json').post()

    # Second load
    DataRequest('bike', '/bike/bike.json').post()
    DataRequest('asset', '/fleet/asset.json').post()
    DataRequest('metadata', '/rider/metadata.json').post()
    DataRequest('joint', '/route/joint.json').post()
    DataRequest('stop', '/stop/stop.json').post()
    # !DataRequest('user', '/user/user.json').post_user()!

    # Third load
    DataRequest('bike_gps', '/bike/bike_gps.json').post()
    DataRequest('lock', '/bike/lock.json').post()
    DataRequest('checkinout', '/checkinout.json').post()
    DataRequest('entry', '/rider/entry.json').post()
    DataRequest('schedule', '/route/schedule.json').post()
    DataRequest('segment', '/route/segment.json').post()
    DataRequest('shelter', '/stop/shelter.json').post()
    DataRequest('sign', '/stop/sign.json').post()
    DataRequest('stop_seq', '/route/stop_seq.json').post()

    # Fourth load
    DataRequest('segment_order', '/route/segment_order.json').post()


# bulk_post()
