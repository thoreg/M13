# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.db import connection

from m13.utils.db.fetch import dictfetchall
from sale.models import Category, TransactionsByDay


class TransactionAggregationService():
    """
    Group all transaction per day and product category to get an easy overview
    per category in the charts.

    """
    def __init__(self, logger):
        self.log = logger

    def aggregate_transactions_by_category_and_day(self, category, begin=None, end=None, dryrun=True):
        self.log.info('   aggregate category: {}'.format(category))
        params = {
            'category': category,
        }

        if begin and end:
            begin = datetime.strptime(begin, '%Y-%m-%d') - timedelta(days=1)
            begin = datetime.strftime(begin, '%Y-%m-%d')
            params['period'] = "AND _time > '{}' and _time <= '{}'".format(begin, end)
        else:
            params['period'] = ''

        with connection.cursor() as cursor:
            cmd = """
                SELECT
                    to_char(_time, 'YYYY-MM-DD') AS day,
                    c.name AS category,
                    SUM(t.turnover) AS turnover
                FROM
                    sale_transaction AS t
                JOIN sale_product AS p
                    ON p.sku = t.product_id
                JOIN sale_category AS c
                    ON c.id = p.category_id

                WHERE c.name = '{category}'
                {period}
                GROUP BY day, category
                ORDER BY day desc
            """.format(**params)

            cursor.execute(cmd)
            rows = dictfetchall(cursor)

        self.log.info('    found {} entries - dryrun: {}'.format(len(rows), dryrun))

        all_categories = Category.objects.all()
        if rows and not dryrun:
            objects_to_create = []
            for row in rows:
                self.log.info(row)
                obj = TransactionsByDay(_time=row['day'],
                                        category=all_categories.get(name=row['category']),
                                        turnover=row['turnover'])
                objects_to_create.append(obj)

            TransactionsByDay.objects.bulk_create(objects_to_create)

        return rows
