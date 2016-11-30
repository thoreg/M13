# -*- coding: utf-8 -*-

import json
import os
import time
from urllib.error import HTTPError

import bottlenose.api
from amazon.api import AmazonAPI
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from sale.models import Product, SalesRankHistory

AMAZON_ACCESS_KEY = os.environ['AMAZON_ACCESS_KEY']
AMAZON_SECRET_KEY = os.environ['AMAZON_SECRET_KEY']
AMAZON_ASSOC_TAG = os.environ['AMAZON_ASSOC_TAG']

WAIT_PERIODS_IN_SECONDS = [1, 2, 3, 5, 8, 13]


class SalesRankFetchService():

    def __init__(self, log):
        self.log = log
        self.api_amazon_de = AmazonAPI(AMAZON_ACCESS_KEY,
                                       AMAZON_SECRET_KEY,
                                       AMAZON_ASSOC_TAG,
                                       region="DE")

    def get_all_salesranks(self):
        """
        Use the amazon product API to receive the salesrank and the price for
        each of our products. Because the service is not always responding
        deterministic we will try in case of error for six times to get the
        corresponding value. At usual the second try is getting a result.

        """
        number_of_fetched_salesrank = 0
        products = Product.objects.all()
        for product in products:

            item = None
            self.log.info('Lookup: {}'.format(product.asin))

            for period in WAIT_PERIODS_IN_SECONDS:
                try:
                    item = self.api_amazon_de.lookup(ItemId=product.asin)
                    break

                except HTTPError:
                    self.log.info('Error occured, wait no for: {} seconds'.format(period))
                    time.sleep(period)

            if item and item.sales_rank:
                self.log.info('  Got salesrank: {}'.format(item.sales_rank))
                self.log.info('  Got price: {}'.format(item.price_and_currency[0]))

                price = item.price_and_currency[0]
                if price:
                    salesrank_history_entry = SalesRankHistory(
                        product=product, price=price, salesrank=item.sales_rank)
                    salesrank_history_entry.save()
                    number_of_fetched_salesrank += 1

        self.log.info('Number of fetched salesrank: {}'.format(number_of_fetched_salesrank))
