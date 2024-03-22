# Don't let IntelliJ reformat move the "from" line from the top
from locust import HttpUser, between, tag, task

import datetime
import json
import random
import uuid

#
# This page was useful: https://www.linode.com/docs/guides/load-testing-with-locust/
#
class LoadSimulator(HttpUser):
    wait_time = between(0.1, 0.5)
    json_headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    first_name_set = (
        "Abigail", "Alice", "Anna", "Avery", "Cameron", "Carter", "Catherine", "Charles", "Christopher", "David",
        "Diana", "Dylan", "Elizabeth", "Emily", "Emma", "Evelyn", "Frances", "Grace", "Hannah", "James", "Jane", "John",
        "Jordan", "Joseph", "Julia", "Laura", "Logan", "Margaret", "Mary", "Michael", "Noah", "Olivia", "Parker",
        "Quinn", "Richard", "Riley", "River", "Robert", "Rose", "Rowan", "Ryan", "Thomas", "Victoria", "William"
    )
    last_name_set = (
        "Anderson", "Brown", "Clark", "Davis", "Garcia", "Gonzales", "Harris", "Hernandez", "Jackson", "Johnson",
        "Jones", "Lee", "Lewis", "Lopez", "Martin", "Martinez", "Miller", "Moore", "Perez", "Ramirez", "Robinson",
        "Rodriguez", "Sanchez", "Smith", "Taylor", "Thomas", "Thompson", "White", "Williams", "Wilson"
    )
    company_set = (
        'Amazon', 'Apple', 'Facebook', 'Google', 'Microsoft', 'Netflix', 'Yugabyte'
    )
    word_set = (
        'Lorem', 'ipsum', 'dolor', 'sit', 'amet,', 'consectetur', 'adipiscing', 'elit,', 'sed', 'do', 'eiusmod',
        'tempor', 'incididunt', 'ut', 'labore', 'et', 'dolore', 'magna', 'aliqua.'
    )

    @task
    @tag('getCache')
    def get_cache(self):
        random_id = random.randint(1, 1000000)
        cache_id = f'cdd7cacd-8e0a-4372-8ceb-{random_id:012}'
        self.client.get(f'/api/cache/{cache_id}', name="/api/cache/{cache_id}")

    @task
    @tag('getCacheWithTTL')
    def get_cache_with_ttl(self):
        random_id = random.randint(1, 1000000)
        cache_id = f'cdd7cacd-8e0a-4372-8ceb-{random_id:012}'
        self.client.get(f'/api/cache/alt/{cache_id}?ttl=300', name='/api/cache/alt/{cache_id}?ttl=300')

    @task
    @tag('saveCache')
    def post_cache(self):
        self.client.post(f'/api/cache?ttl=60',
                         data=json.dumps(LoadSimulator.random_json()),
                         headers=LoadSimulator.json_headers)

    # @task
    @tag('deviceTracker2')
    def patch_device_tracker2(self):
        num = random.randint(1, 11000)
        num2 = random.randint(1, 60)
        deviceId = 'cdd7cacd-8e0a-4372-8ceb-' + str(num).zfill(12)
        mediaId = '48d1c2c2-0d83-43d9-' + str(num2).zfill(4) + '-' + str(num).zfill(12)
        status = 'MOD-' + str(random.randint(0, 3))
        jsond = {
            'deviceId': deviceId,
            'mediaId': mediaId,
            'status': status
        }
        self.client.patch(f'/api/tracker', data=json.dumps(jsond), headers=LoadSimulator.json_headers)

    # this was a useful blog: https://www.lambdatest.com/blog/python-random-string/

    @staticmethod
    def random_json() -> dict:
        json_data = {
            'guid': str(uuid.uuid4()),
            'isActive': LoadSimulator.random_boolean(.90),
            'balance': LoadSimulator.random_money(),
            'picture': 'http://placehold.it/32x32',
            'age': random.randint(18, 99),
            'name': LoadSimulator.random_name(),
            'company': random.choice(LoadSimulator.company_set),
            'phone': LoadSimulator.random_phone(),
            'address': '104 Newkirk Avenue, Echo, Pennsylvania, 2279',
            'about': LoadSimulator.random_words(),
            'registered': LoadSimulator.random_date().isoformat(),
            'latitude': LoadSimulator.random_latitude(),
            'longitude': LoadSimulator.random_longitude(),
            'cars': [
                {'model': 'BMW 230', 'mpg': 27.5},
                {'model': 'Ford Edge', 'mpg': 24.1}
            ]
        }
        return json_data

    @staticmethod
    def random_name() -> str:
        return random.choice(LoadSimulator.first_name_set) + ' ' + random.choice(LoadSimulator.last_name_set)

    @staticmethod
    def random_words(max_words=50, min_words=10) -> str:
        return ' '.join(random.choice(LoadSimulator.word_set)
                        for _ in range(random.randint(min_words, max_words)))

    @staticmethod
    def random_date(start=datetime.datetime(2000, 1, 1), end=datetime.datetime.now()):
        return start + (end - start) * random.random()

    @staticmethod
    def random_phone() -> str:
        area_code = random.randint(200, 999)
        line_number = random.randint(0, 9999)
        return f'+1 ({area_code}) 555-{line_number:04}'

    @staticmethod
    def random_boolean(weight=0.5) -> bool:
        return random.random() < weight

    @staticmethod
    def random_longitude(min_longitude=-180.0, max_longitude=180.0) -> float:
        return random.uniform(min_longitude, max_longitude)

    @staticmethod
    def random_latitude(min_latitude=-90.0, max_latitude=90.0) -> float:
        return random.uniform(min_latitude, max_latitude)

    @staticmethod
    def random_money(currency_symbol='$', min_money=0.0, max_money=999999.0) -> str:
        return '{}{:,.2f}'.format(currency_symbol, random.uniform(min_money, max_money))
