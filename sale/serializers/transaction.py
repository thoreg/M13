
from rest_framework import serializers

from ..models import Transaction


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


class TransactionStatsSerializer(serializers.HyperlinkedModelSerializer):
    year = serializers.SerializerMethodField()
    month = serializers.SerializerMethodField()
    day = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = (
            'day',
            'month',
            'year',
            'total',

        )

    def get_year(self, obj):
        return obj._time.strftime('%y')

    def get_month(self, obj):
        return obj._time.strftime('%m')

    def get_day(self, obj):
        return obj._time.strftime('%d')
