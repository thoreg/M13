# -*- coding: utf-8 -*-
"""
The report about active offers comes on amazon_de with the following fields:

item-name
item-description
listing-id
seller-sku
price
quantity
open-date
image-url
item-is-marketplace
product-id-type
zshop-shipping-fee
item-note
item-condition
zshop-category1
zshop-browse-path
zshop-storefront-feature
asin1
asin2
asin3
will-ship-internationally
expedited-shipping
zshop-boldface
product-id
bid-for-featured-placement
add-delete
pending-quantity
fulfillment-channel

"""
import csv
import logging

from django.core.management.base import BaseCommand

from sale.models import Product, ProductDescriptionDE

log = logging.getLogger('main')


def read_file_line_by_line(file):
    reader = csv.reader(file, delimiter='\t')
    for line in reader:
        yield line


def process_line(line):
    """
    Create an entry in the transaction table with information of interest.

    """
    log.debug(line)

    sku = line[3]
    values = {
        'name': line[0],
        'sku': sku,
        'asin': line[16],

    }

    product, created_product = Product.objects.update_or_create(**values)
    log.debug('Created Product: {}'.format(created_product))

    values = {
        'product': product,
        'description': line[1],
    }
    obj, created_description = ProductDescriptionDE.objects.update_or_create(**values)
    log.debug('Created Description: {}'.format(created_description))

    return created_product, created_description


def process_file(file):
    count = 1
    new_created_product_count = 0
    new_created_description_count = 0

    for line in read_file_line_by_line(file):
        # Ignore 'header' line of csv file
        if count > 1:
            created_product, created_description = process_line(line)
            if created_product:
                new_created_product_count += 1
            if created_description:
                new_created_description_count += 1
        else:
            log.debug(line)

        count += 1

    log.info('- Finished -\n {} lines successfully processed.'.format(count))
    log.info('{} new product entries created'.format(new_created_product_count))
    log.info('{} new description entries created'.format(new_created_product_count))


class Command(BaseCommand):

    def add_arguments(self, parser):
        # Positional argument
        parser.add_argument('filename', nargs=1)

    def handle(self, *args, **options):

        verbosity = options.get('verbosity')

        if verbosity == 1:  # default
            logging.getLogger('main').setLevel(logging.WARN)
        if verbosity > 1:
            logging.getLogger('main').setLevel(logging.INFO)
        if verbosity > 2:
            logging.getLogger('main').setLevel(logging.DEBUG)

        log.debug("args: {}".format(args))
        log.debug("options: {}".format(options))

        filename = options['filename'][0]
        log.info('Processing: {}'.format(filename))

        with open(filename, 'r', encoding='iso-8859-1') as file:
            process_file(file)
