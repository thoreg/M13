# -*- coding: utf-8 -*-

import logging
import os

from django.core.management.base import BaseCommand

from sale.services.salesrank import SalesRankFetchService

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

        salesrank_fetch_service = SalesRankFetchService(log)
        salesrank_fetch_service.get_all_salesranks()
