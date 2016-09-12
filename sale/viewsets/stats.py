from rest_framework import generics

from ..models import Transaction
from ..serializers import TransactionDayStatsSerializer


class TransactionDayStatsList(generics.ListAPIView):
    serializer_class = TransactionDayStatsSerializer

    def get_queryset(self):
        queryset = Transaction.objects.raw('''
            SELECT
                row_number() over() AS id,
                EXTRACT(YEAR FROM _time) AS year,
                EXTRACT(MONTH FROM _time) AS month,
                EXTRACT(DAY FROM _time) AS day,
                SUM(total) AS sum_total
            FROM sale_transaction
            WHERE
                _type = 'Bestellung'
            GROUP BY year, month, day
            ORDER BY year DESC, month DESC, day DESC;
        ''')

        return queryset
