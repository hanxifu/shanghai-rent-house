import time
from random import random

import requests
from lxml import etree

from rent_house import db
from rent_house.models import City, District
from . import PLATFORM
from .header import create_headers
from .utils import get_or_create
from .xpath import DISTRICTS_XPATH


class BaseCrawler:
    @staticmethod
    def random_delay():
        time.sleep(random.randint(0, 16))


class CityCrawler(BaseCrawler):
    # Now we only support Shanghai, so this crawler is skipped.
    pass


class DistrictCrawler(BaseCrawler):
    def __init__(self, city_name):
        self.city = City.query.filter_by(full_name=city_name).first()

    def get_districts(self):
        url = f'https://{self.city.abbr_name}.{PLATFORM}.com/zufang/'
        headers = create_headers()
        response = requests.get(url, timeout=10, headers=headers)
        root = etree.HTML(response.content)
        elements = root.findall(DISTRICTS_XPATH)
        for elem in elements:
            if 'rel' in elem.attrib:
                continue

            city_id = self.city.id
            name = elem.attrib['href'].split('/')[-2]
            name_zh = elem.text
            district, created = get_or_create(db.session, District,
                                              city_id=city_id, name=name, name_zh=name_zh)
            if created:
                db.session.add(district)
                db.session.commit()
