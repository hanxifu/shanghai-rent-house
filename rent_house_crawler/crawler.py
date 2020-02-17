import time
from random import random
from typing import Union

import requests
from lxml import etree

from rent_house import db
from rent_house.models import City, District, Bizcircle, Line
from . import PLATFORM
from .errors import ParameterNotAllowedError
from .header import create_headers
from .utils import get_or_create, get_or_create_m2m
from .xpath import DISTRICTS_XPATH, BIZCIRCLES_XPATH


class BaseCrawler:
    @staticmethod
    def random_delay():
        time.sleep(random.randint(0, 16))


class CityCrawler(BaseCrawler):
    # Now we only support Shanghai, so this crawler is skipped.
    pass


class DistrictCrawler(BaseCrawler):
    def __init__(self, city_instance: City):
        self.city = city_instance

    def get_districts(self):
        url = f'https://{self.city.name_abbr}.{PLATFORM}.com/zufang/'
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
            get_or_create(db.session, District, city_id=city_id, name=name, name_zh=name_zh)


class BizcircleCrawler(BaseCrawler):
    def __init__(self, city_instance: City, father_instance: Union[District, Line]):
        self.city = city_instance
        if isinstance(father_instance, District):
            self.father_type = District
        elif isinstance(father_instance, Line):
            self.father_type = Line
        else:
            raise ParameterNotAllowedError('Parameter "father" should be a District or Line instance.')
        self.father = father_instance

    def get_bizcircle(self):
        url = f'https://{self.city.name_abbr}.{PLATFORM}.com/zufang/{self.father.name}/'
        headers = create_headers()
        response = requests.get(url, timeout=10, headers=headers)
        root = etree.HTML(response.content)
        elements = root.findall(BIZCIRCLES_XPATH)
        for elem in elements:
            if 'rel' in elem.attrib:
                continue

            name = elem.attrib['href'].split('/')[-2]
            name_zh = elem.text

            get_or_create_m2m(db.session, Bizcircle, self.father.bizcircles,
                              city_id=self.city.id, name=name, name_zh=name_zh)
