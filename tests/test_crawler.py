from unittest import TestCase

from rent_house.models import City
from rent_house_crawler.crawler import DistrictCrawler


class TestDistrictCrawler(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        test_city = 'shanghai'
        test_city_districts = 16

        cls._crawler = DistrictCrawler(test_city)
        cls._city = City.query.filter_by(full_name=test_city).first()
        cls._districts_amount = test_city_districts

    def test_get_districts(self):
        self.assertIsNone(self._crawler.get_districts())
        self.assertEqual(len(self._city.districts), self._districts_amount)
