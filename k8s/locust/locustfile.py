# Don't let IntelliJ reformat move the "from" line from the top
from locust import HttpUser, between, tag, task

import datetime
import json
import random
import uuid


class LoadSimulator(HttpUser):
    wait_time = between(0.1, 0.5)
    json_headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    random_company = ("Amazon", "Apple", "Facebook", "Google", "Microsoft", "Yugabyte")
    random_words = (
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
    def get_cache_ttl(self):
        random_id = random.randint(1, 1000000)
        cache_id = f'cdd7cacd-8e0a-4372-8ceb-{random_id:012}'
        self.client.get(f'/api/cache/alt/{cache_id}?ttl=300', name='/api/cache/alt/{cacheId}?ttl=300')

    @task
    @tag('saveCache')
    def post_cache(self):
        json_data = {
            "guid": str(uuid.uuid4()),
            "isActive": random.random() < .90,
            "balance": '${:,.2f}'.format(random.uniform(0.0, 999999.0)),
            "picture": "http://placehold.it/32x32",
            "age": random.randint(18, 99),
            "name": "Gale Whitney",
            "company": random.choice(LoadSimulator.random_company),
            "phone": LoadSimulator.random_phone(),
            "address": "104 Newkirk Avenue, Echo, Pennsylvania, 2279",
            "about": ' '.join(random.sample(LoadSimulator.random_words, 15)),
            "registered": LoadSimulator.random_date().isoformat(),
            "latitude": random.uniform(-180.0, 180.0),
            "longitude": random.uniform(-9.0, 90.0),
            "cars": [
                {"model": "BMW 230", "mpg": 27.5},
                {"model": "Ford Edge", "mpg": 24.1}
            ]
        }
        self.client.post(f"/api/cache?ttl=60", data=json.dumps(json_data), headers=LoadSimulator.json_headers)

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
        self.client.patch(f"/api/tracker", data=json.dumps(jsond), headers=LoadSimulator.json_headers)

    @staticmethod
    def random_date():
        start = datetime.datetime(2000, 1, 1)
        return start + (datetime.datetime.now() - start) * random.random()

    @staticmethod
    def random_phone():
        area_code = random.randint(200, 999)
        line_number = random.randint(0, 9999)
        return f'+1 ({area_code}) 555-{line_number:04}'
