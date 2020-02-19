import os
import time
import traceback
from concurrent import futures
from random import random
from typing import Union

from rent_house import db
from rent_house.models import City, District, Bizcircle, Line, Community
from . import PLATFORM
from .errors import ParameterNotAllowedError
from .header import get_root_element
from .utils import get_or_create, add_m2m_relationship
from .xpath import DISTRICTS_XPATH, BIZCIRCLES_XPATH, COMMUNITY_PAGES_XPATH, COMMUNITY_INFO_XPATH


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
        root = get_root_element(f'https://{self.city.name_abbr}.{PLATFORM}.com/zufang/')
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
        """
        Bizcircle instance can be under Line instance or District instance. Now
        we only support District instance.
        TODO Line instance should also be supported.
        """
        self.city = city_instance
        if isinstance(father_instance, District):
            self.father_type = District
        elif isinstance(father_instance, Line):
            self.father_type = Line
        else:
            raise ParameterNotAllowedError('Parameter "father" should be a District or Line instance.')
        self.father = father_instance

    def get_bizcircle(self):
        root = get_root_element(f'https://{self.city.name_abbr}.{PLATFORM}.com/zufang/{self.father.name}/')
        elements = root.findall(BIZCIRCLES_XPATH)
        bizcircle_instances = []
        for elem in elements:
            if 'rel' in elem.attrib:
                continue

            name = elem.attrib['href'].split('/')[-2]
            name_zh = elem.text

            instance, _ = get_or_create(db.session, Bizcircle,
                                        city_id=self.city.id, name=name, name_zh=name_zh)
            bizcircle_instances.append(instance)
        add_m2m_relationship(db.session, self.father.bizcircles, bizcircle_instances)


# Now we use concurrent.futures to do parallel crawling.
MAX_WORKERS = os.cpu_count() + 4


class CommunityCrawler(BaseCrawler):
    def __init__(self, city_instance: City, bizcircle_instance: Bizcircle):
        self.city = city_instance
        self.bizcircle = bizcircle_instance
        self.base_url = f'https://{self.city.name_abbr}.{PLATFORM}.com/xiaoqu/'
        self.total_pages = 1
        self.workers = MAX_WORKERS

    def get_total_pages(self) -> int:
        root = get_root_element(self.base_url + f'{self.bizcircle.name}/')
        element = root.find(COMMUNITY_PAGES_XPATH)
        return eval(element.attrib['page-data'])['totalPage']

    def get_community(self):
        self.total_pages = self.get_total_pages()
        self.workers = min(self.workers, self.total_pages)
        urls = [self.base_url + f'{self.bizcircle.name}/pg{i}' for i in range(1, self.total_pages + 1)]

        community_instances = []
        with futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
            future_roots = {executor.submit(self._get_community_each_page, url): url for url in urls}
            for future in futures.as_completed(future_roots):
                url = future_roots[future]
                try:
                    community_instances.extend(future.result())
                except Exception as e:
                    print(f'{url} generated an exception: {e}')
                    traceback.print_exc()

        # Here we use db.session.merge() to make the thread object to local object.
        # Otherwise it will throw "Object is already attached to session" exception.
        for instance in community_instances:
            local_instance = db.session.merge(instance)
            if local_instance not in self.bizcircle.communities:
                self.bizcircle.communities.append(local_instance)
        db.session.commit()

    def _get_community_each_page(self, url: str):
        root = get_root_element(url)
        elements = root.findall(COMMUNITY_INFO_XPATH)
        community_instances = []
        for elem in elements:
            info_elem = elem.getchildren()[1]
            name_elem = info_elem.find('.//div[@class="title"]/a')
            name = name_elem.attrib['href'].split('/')[-2]
            name_zh = name_elem.text

            year_elem = info_elem.find('.//div[@class="positionInfo"]')
            '''
            Here's the lianjia website's mistake. They wrote something like this:

            <div>
                <span>foo</span>
                <a>bar</a>
                year-we-need
            </div>

            I have to use itertext() and some ugly code to deal with it.`
            '''
            text = [i for i in year_elem.itertext()][-1]
            try:
                year = int(text.split('\xa0')[-1].split('年建成')[0])
            except ValueError:
                year = 1970

            price_elem = elem.getchildren()[2]
            total_price_elem = price_elem.find('.//div[@class="xiaoquListItemPrice"]/div[@class="totalPrice"]/span')
            try:
                price = int(total_price_elem.text)
            except ValueError:
                price = 0

            community_instance, _ = get_or_create(db.session, Community,
                                                  city_id=self.bizcircle.city_id, name=name, name_zh=name_zh)
            community_instance.year = year
            community_instance.price = price
            db.session.commit()
            community_instances.append(community_instance)

        # return all the thread object to the main thread.
        return community_instances
