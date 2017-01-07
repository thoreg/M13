import datetime
from decimal import Decimal

import pytest
from freezegun import freeze_time
from model_mommy import mommy

from sale.models import Product, SalesRankHistory, SalesRankHistoryByDay
from sale.services.salesrankhistory import SalesRankHistoryAggregationService


@pytest.mark.django_db
def test_aggregate_salesrank_history_by_day():
    """
    The salesrank for a product is read every hour and varies during the day.
    Get the average value for the salesrank of a product of the day.
    If `dryrun` is True the calculated values are written to the database.

    """
    srvc = SalesRankHistoryAggregationService()

    salesrank_history_entries = [
        {'time': '2016-10-16', 'sku': 'sku1', 'price': '1.2', 'salesrank': 3},
        {'time': '2016-10-16', 'sku': 'sku1', 'price': '1.2', 'salesrank': 4},
        {'time': '2016-10-17', 'sku': 'sku1', 'price': '1.2', 'salesrank': 4},
        {'time': '2016-10-17', 'sku': 'sku1', 'price': '1.8', 'salesrank': 6},
        {'time': '2016-10-18', 'sku': 'sku1', 'price': '1.2', 'salesrank': 8},
    ]
    for entry in salesrank_history_entries:
        with freeze_time(entry['time']):
            mommy.make(SalesRankHistory,
                       product__sku=entry['sku'],
                       price=entry['price'],
                       salesrank=entry['salesrank'])

    product = Product.objects.get()

    # A single day
    avg_sales_rank = srvc.aggregate_salesrank_history_by_day(
        product, begin='2016-10-17', end='2016-10-18')

    assert avg_sales_rank == [
        {'avg_price': Decimal('1.50'), 'avg_salesrank': 5, 'day': '2016-10-17'}]

    # A period
    avg_sales_rank = srvc.aggregate_salesrank_history_by_day(
        product, begin='2016-10-17', end='2016-10-19')

    assert avg_sales_rank == [
        {'avg_price': Decimal('1.20'), 'avg_salesrank': 8, 'day': '2016-10-18'},
        {'avg_price': Decimal('1.50'), 'avg_salesrank': 5, 'day': '2016-10-17'}]

    # Write calculations to the database
    EXPECTED_AVG_SALESRANK_BY_DAY = [
        {'_time': datetime.datetime(2016, 10, 18, 0, 0),
         'id': 1,
         'price': Decimal('1.20'),
         'product_id': 'sku1',
         'salesrank': 8},
        {'_time': datetime.datetime(2016, 10, 17, 0, 0),
         'id': 2,
         'price': Decimal('1.50'),
         'product_id': 'sku1',
         'salesrank': 5}
    ]

    avg_sales_rank = srvc.aggregate_salesrank_history_by_day(
        product, begin='2016-10-17', end='2016-10-19', dryrun=False)

    all_avg_sales_rank_by_day = SalesRankHistoryByDay.objects.all().order_by('-_time').values()
    assert len(all_avg_sales_rank_by_day) == 2
    for situation, expected in zip(all_avg_sales_rank_by_day, EXPECTED_AVG_SALESRANK_BY_DAY):
        assert situation == expected
