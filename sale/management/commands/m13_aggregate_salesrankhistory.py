# -*- coding: utf-8 -*-

import logging

from django.core.management.base import BaseCommand

from sale.models import Product
from sale.services.salesrankhistory import SalesRankHistoryAggregationService

log = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        verbosity = options.get('verbosity')

        if verbosity == 1:  # default
            log.setLevel(logging.WARN)
        if verbosity > 1:
            log.setLevel(logging.INFO)
        if verbosity > 2:
            log.setLevel(logging.DEBUG)

        srvc = SalesRankHistoryAggregationService()
        for product in Product.objects.all():
            print('Aggregate: {}'.format(product.sku))
            srvc.aggregate_salesrank_history_by_day(product, dryrun=False)
