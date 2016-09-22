# -*- coding: utf-8 -*-
"""
Get the current sales rank for a product with a given ASIN.

"""
import json
import logging
import os
import time

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from selenium import webdriver

from sale.models import Product, SalesRankHistory


AMAZON_INVENTORY_URL = 'https://sellercentral.amazon.de/hz/inventory'


log = logging.getLogger(__name__)


class Command(BaseCommand):

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

        login_button = self.driver.find_element_by_id("signInSubmit")
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

        inventory_table = self.driver.find_element_by_id("myitable")
        soup = BeautifulSoup(inventory_table.get_attribute('innerHTML'))
        all_rows = soup.find_all('tr')

        for row in all_rows:
            if row.find_all('td', attrs={'data-column': "sku"}):
                self.process_row(row)

    def process_row(row):
        sku = ''
        sales_rank = ''
        price = ''

        sku = row.find_all('td', attrs={'data-column': "sku"})[0]
        sku = sku.text.split()[0]

        try:
            sales_rank = row.find_all('td', attrs={'data-column': "sales_rank"})[0]
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
                log.debug("No price found for SKU: {} SalesRank: {}".format(
                    sku, sales_rank))
                return

        price = price.replace(',', '.')
        log.debug("SKU: {} SalesRank: {} Price: {}".format(sku, sales_rank, price))
        product = Product.objects.get(sku=sku)
        sales_rank_history_entry = SalesRankHistory(product=product,
                                                    price=price,
                                                    sales_rank=sales_rank)
        sales_rank_history_entry.save()

    def handle(self, *args, **options):

        verbosity = options.get('verbosity')

        if verbosity == 1:  # default
            log.setLevel(logging.WARN)
        if verbosity > 1:
            log.setLevel(logging.INFO)
        if verbosity > 2:
            log.setLevel(logging.DEBUG)

        log.debug("os.environ['AMAZON_USER_NAME']: {}".format(os.environ['AMAZON_USER_NAME']))
        log.debug("os.environ['AMAZON_PASSWORD']: {}".format(os.environ['AMAZON_PASSWORD']))

        self.login()
        self.get_all_salesranks()
