from unittest import TestCase

from rent_house.models import City, District, Bizcircle
from rent_house_crawler.crawler import DistrictCrawler, BizcircleCrawler, CommunityCrawler


class TestDistrictCrawler(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        test_city = 'shanghai'
        test_city_districts = 16

        cls._city = City.query.filter_by(name=test_city).first()
        cls._crawler = DistrictCrawler(cls._city)
        cls._districts_amount = test_city_districts

    def test_get_districts(self):
        self.assertIsNone(self._crawler.get_districts())
        self.assertEqual(len(self._city.districts), self._districts_amount)


class TestBizcircleCrawler(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        test_city = 'shanghai'
        test_district = 'pudong'
        test_district_bizcircles = 39

        cls._city = City.query.filter_by(name=test_city).first()
        cls._district = District.query.filter_by(city_id=cls._city.id, name=test_district).first()
        cls._crawler = BizcircleCrawler(cls._city, cls._district)
        cls._bizcircles_amount = test_district_bizcircles

    def test_get_bizcircle(self):
        self.assertIsNone(self._crawler.get_bizcircle())
        self.assertEqual(len(self._district.bizcircles), self._bizcircles_amount)


class TestCommunityCrawler(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        test_city = 'shanghai'
        test_bizcircle = 'beicai'
        test_bizcircle_communities = 300

        cls._city = City.query.filter_by(name=test_city).first()
        cls._bizcircle = Bizcircle.query.filter_by(city_id=cls._city.id, name=test_bizcircle).first()
        cls._crawler = CommunityCrawler(cls._city, cls._bizcircle)
        cls._bizcircles_amount = test_bizcircle_communities

    def test_get_bizcircle(self):
        self.assertIsNone(self._crawler.get_community())
        self.assertAlmostEqual(len(self._bizcircle.communities), self._bizcircles_amount, delta=10)
