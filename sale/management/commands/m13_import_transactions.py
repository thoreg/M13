"""
The report about transactions comes on amazon_de with the following fields:

"Datum/Uhrzeit",
"Abrechnungsnummer",
"Typ",
"Bestellnummer",
"SKU",
"Beschreibung",
"Menge",
"Marketplace",
"Versand",
"Ort der Bestellung",
"Bundesland",
"Postleitzahl",
"Umsätze",
"Gutschrift für Versandkosten",
"Gutschrift für Geschenkverpackung",
"Rabatte aus Werbeaktionen",
"Verkaufsgebühren",
"Gebühren zu Versand durch Amazon",
"Andere Transaktionsgebühren",
"Andere",
"Gesamt"

"""
import csv
import logging
from decimal import Decimal

from dateutil import parser
from django.core.management.base import BaseCommand

from sale.models import Transaction

log = logging.getLogger('main')


def read_file_line_by_line(file):
    reader = csv.reader(file)
    for line in reader:
        yield line


def process_line(line):
    """
    Create an entry in the transaction table with information of interest.

    """
    log.debug(line)
    values = {
        # line[0] => 01.01.2015 20:29:20 GMT+00:00
        '_time': parser.parse(line[0]),
        # line[1] => "Abrechnungsnummer"
        '_type': line[2],
        'order_id': line[3],
        'sku': line[4],
        # line[5] => description
        'amount': line[6] or 0,
        'marketplace': line[7],
        'dispatch_type': line[8],
        'city': line[9],
        # line[10] => Bundesland
        'postal_code': line[11],
        'turnover': Decimal(line[12].replace('.', '').replace(',', '.')),
        'voucher_shipping_costs': Decimal(line[13].replace('.', '').replace(',', '.')),
        # line[14] => 'Gutschrift für Geschenkverpackung',
        # line[15] => 'Rabatte aus Werbeaktionen',
        'charge': Decimal(line[16].replace('.', '').replace(',', '.')),
        'charge_fba': Decimal(line[17].replace('.', '').replace(',', '.')),
        'charge_other': Decimal(line[18].replace('.', '').replace(',', '.')),
        'other': Decimal(line[19].replace('.', '').replace(',', '.')),
        'total': Decimal(line[20].replace('.', '').replace(',', '.')),
    }

    obj, created = Transaction.objects.update_or_create(**values)
    log.debug('Created: {}'.format(created))

    return created


def process_file(file):
    count = 1
    new_created_lines_count = 0

    for line in read_file_line_by_line(file):
        # Ignore 'header' line of csv file
        if count > 1:
            created = process_line(line)
            if created:
                new_created_lines_count += 1

        count += 1

    log.info('- Finished -\n {} lines successfully processed.'.format(count))
    log.info('{} new entries created'.format(new_created_lines_count))


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

        with open(filename, 'r') as file:
            process_file(file)
