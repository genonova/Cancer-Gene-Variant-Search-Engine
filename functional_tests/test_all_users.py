# -*- coding: utf-8 -*-
from selenium import webdriver
from django.core.urlresolvers import reverse
from django.contrib.staticfiles.testing import LiveServerTestCase
import unittest


class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome() # place to get drivers: https://sites.google.com/a/chromium.org/chromedriver/downloads
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def get_full_url(self, namespace):
        return self.live_server_url + reverse(namespace)

    # def test_home_title(self):
    #     self.browser.get(self.get_full_url("home"))
    #     self.assertIn("TaskBuster", self.browser.title)
    #
    # def test_h1_css(self):
    #     self.browser.get(self.get_full_url("home"))
    #     h1 = self.browser.find_element_by_tag_name("h1")
    #     self.assertEqual(h1.value_of_css_property("color"),
    #                      "rgba(200, 50, 255, 1)")

    # def test_it_worked(self):
    #     self.browser.get('http://localhost:8000')
    #     self.assertIn('Page not found', self.browser.title)

    # def test_index_files(self):
    #     self.browser.get(self.live_server_url + "/robots.txt")
    #     self.assertNotIn("Not Found", self.browser.title)
    #     self.browser.get(self.live_server_url + "/humans.txt")
    #     self.assertNotIn("Not Found", self.browser.title)

if __name__ == '__main__':
    unittest.main()

