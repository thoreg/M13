# -*- coding: utf-8 -*-

import json
import logging
import os
import time

from bs4 import BeautifulSoup
from selenium import webdriver

from sale.models import Product, SalesRankHistory

AMAZON_INVENTORY_URL = 'https://sellercentral.amazon.de/hz/inventory'


class SalesRankFetchService():
    """
    Get the current sales rank for all procducts of the inventory page. Ignore
    products without a valid sales_rank information ('-') or products with variants.

    """

    def __init__(self, log):
        self.log = log
        self.number_of_fetched_salesrank = 0

        print(self.log.__dict__)

    def login(self):
        """
        Login to the amazon seller central website via selenium.

        """
        self.driver = webdriver.Firefox()
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

        self.log.info('Number of fetched sales_rank: {}'.format(self.number_of_fetched_salesrank))

    def process_row(self, row):
        sku = ''
        sales_rank = ''
        price = ''

        sku = row.find_all('td', attrs={'data-column': "sku"})[0]
        sku = sku.text.split()[0]

        try:
            sales_rank = row.find_all('td', attrs={'data-column': 'sales_rank'})[0]
            if sales_rank:
                sales_rank = sales_rank.text.split()[0].replace('.', '')

        except IndexError:
            return

        if sales_rank == '-':
            return

        price = row.find_all('span', attrs={'data-myitable-inline-changed': True})
        try:
            price = json.loads(price[1]['data-myitable-inline-changed'])['original']
        except IndexError:
            try:
                price = json.loads(price[0]['data-myitable-inline-changed'])['original']
            except IndexError:
                self.log.debug('No price found for SKU: {} SalesRank: {}'.format(
                    sku, sales_rank))
                return

        price = price.replace(',', '.')

        self.log.debug('SKU: {} SalesRank: {} Price: {}'.format(sku, sales_rank, price))

        product = Product.objects.get(sku=sku)
        sales_rank_history_entry = SalesRankHistory(product=product,
                                                    price=price,
                                                    sales_rank=sales_rank)
        sales_rank_history_entry.save()

        self.number_of_fetched_salesrank += 1
