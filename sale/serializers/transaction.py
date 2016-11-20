
from rest_framework import serializers

from ..models import Transaction, TransactionsByDay


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    year = serializers.SerializerMethodField()
    month = serializers.SerializerMethodField()
    day = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = (
            '_time',
            '_type',
            'day',
            'month',
            'order_id',
            'sku',
            'total',
            'year',
        )

    def get_year(self, obj):
        return obj._time.strftime('%y')

    def get_month(self, obj):
        return obj._time.strftime('%m')

    def get_day(self, obj):
        return obj._time.strftime('%d')


class TransactionsByDaySerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    turnover = serializers.SerializerMethodField()

    class Meta:
        model = TransactionsByDay
        fields = (
            'date',
            'turnover',
        )

    def get_date(self, obj):
        return obj._time.strftime('%Y-%m-%d')

    def get_turnover(self, obj):
        return obj.turnover
