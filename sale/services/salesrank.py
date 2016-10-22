# -*- coding: utf-8 -*-

import json
import os
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from sale.models import Product, SalesRankHistory

AMAZON_INVENTORY_URL = 'https://sellercentral.amazon.de/hz/inventory'

# Amazon seems not to like the default user agent of phantomjs
# With the following user agent settings it is possible to login via phantomjs
# otherwise we get the error message to enable cookies and the login is not
# possible
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " +
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36"
)

dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = USER_AGENT


class SalesRankFetchService():
    """
    Get the current sales rank for all procducts of the inventory page. Ignore
    products without a valid salesrank information ('-') or products with variants.

    """

    def __init__(self, log, driver):
        self.log = log
        self.number_of_fetched_salesrank = 0

        if driver == "firefox":
            self.driver = webdriver.Firefox()

        else:
            self.driver = webdriver.PhantomJS(desired_capabilities=dcap)
            self.driver.set_window_size(1024, 800)

        self.driver.cookies_enabled = True

    def login(self):
        """
        Login to the amazon seller central website via selenium.

        """
        self.driver.get(os.environ['AMAZON_URL'])

        email = self.driver.find_element_by_id("ap_email")
        password = self.driver.find_element_by_id("ap_password")

        email.send_keys(os.environ['AMAZON_USER_NAME'])
        password.send_keys(os.environ['AMAZON_PASSWORD'])
        time.sleep(1)

        login_button = self.driver.find_element_by_id('signInSubmit')
        login_button.click()

    def get_all_salesranks(self):
        """
        Visit the inventory page and grep for salesrank information - it might
        be necessary that you have to enable that column first.

        Save the current salesrank information and the current price.

        """
        self.driver.get(AMAZON_INVENTORY_URL)
        # Wait ten seconds to give the inventory page time to load
        for seconds in range(1, 11):
            time.sleep(1)

        inventory_table = self.driver.find_element_by_id('myitable')
        soup = BeautifulSoup(inventory_table.get_attribute('innerHTML'), 'html.parser')
        all_rows = soup.find_all('tr')

        for row in all_rows:
            if row.find_all('td', attrs={'data-column': 'sku'}):
                self.process_row(row)

        self.log.info('Number of fetched salesrank: {}'.format(self.number_of_fetched_salesrank))

    def process_row(self, row):
        sku = ''
        salesrank = ''
        price = ''

        sku = row.find_all('td', attrs={'data-column': "sku"})[0]
        sku = sku.text.split()[0]

        try:
            salesrank = row.find_all('td', attrs={'data-column': 'sales_rank'})[0]
            if salesrank:
                salesrank = salesrank.text.split()[0].replace('.', '')

        except IndexError:
            return

        if salesrank == '-':
            return

        price = row.find_all('span', attrs={'data-myitable-inline-changed': True})
        try:
            price = json.loads(price[1]['data-myitable-inline-changed'])['original']
        except IndexError:
            try:
                price = json.loads(price[0]['data-myitable-inline-changed'])['original']
            except IndexError:
                self.log.debug('No price found for SKU: {} SalesRank: {}'.format(
                    sku, salesrank))
                return

        price = price.replace(',', '.')

        self.log.debug('SKU: {} SalesRank: {} Price: {}'.format(sku, salesrank, price))

        product = Product.objects.get(sku=sku)
        salesrank_history_entry = SalesRankHistory(product=product,
                                                   price=price,
                                                   salesrank=salesrank)
        salesrank_history_entry.save()

        self.number_of_fetched_salesrank += 1
