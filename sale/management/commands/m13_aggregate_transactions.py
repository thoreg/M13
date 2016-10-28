# -*- coding: utf-8 -*-

import logging

from django.core.management.base import BaseCommand

from sale.models import Category
from sale.services.transaction import TransactionAggregationService

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

        srvc = TransactionAggregationService(logger=log)

        for category in Category.objects.all():
            log.info('Aggregate Category: {}'.format(category))
            srvc.aggregate_transactions_by_category_and_day(category, dryrun=False)
