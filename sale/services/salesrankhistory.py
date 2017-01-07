# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.db import connection, transaction

from m13.utils.db.fetch import dictfetchall
from sale.models import Product, SalesRankHistoryByDay


class SalesRankHistoryAggregationService():
    """
    The salesrank of a product changes during the day, depending on sales, sales
    from other sellers etc. Calculate the average salesrank for the product.
    If not dryrun then write the result to the database.

    """
    def __init__(self, log=None):
        self.log = log

    @transaction.atomic
    def aggregate_salesrank_history_by_day(self, product, begin=None, end=None, dryrun=True):
        """
        Aggregate all salesrank history entries per day from 'begin' till 'end'
        but not including 'end'.

        """
        if self.log:
            self.log.info('   aggregate sku: {}'.format(product.sku))

        params = {
            'sku': product.sku,
        }

        if begin and end:
            params['period'] = "AND _time >= '{}' and _time < '{}'".format(begin, end)
        else:
            params['period'] = ''

        SalesRankHistoryByDay.objects.filter(product=product).delete()

        with connection.cursor() as cursor:
            cmd = """
                SELECT
                    to_char(_time, 'YYYY-MM-DD') AS day,
                    AVG(salesrank)::integer AS avg_salesrank,
                    round(AVG(price)::numeric, 2) AS avg_price
                FROM
                    sale_salesrankhistory
                WHERE product_id = '{sku}'
                {period}
                GROUP BY day
                ORDER BY day desc
            """.format(**params)

            cursor.execute(cmd)
            rows = dictfetchall(cursor)

        if self.log:
            self.log.info('    found {} entries - dryrun: {}'.format(len(rows), dryrun))

        if rows and not dryrun:
            objects_to_create = []
            for row in rows:
                obj = SalesRankHistoryByDay(product=product,
                                            price=row['avg_price'],
                                            salesrank=row['avg_salesrank'],
                                            _time=row['day'])
                objects_to_create.append(obj)

            SalesRankHistoryByDay.objects.bulk_create(objects_to_create)

        return rows
