from rest_framework import serializers

from ..models import SalesRankHistory, SalesRankHistoryByDay


class SalesRankHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesRankHistory
        fields = (
            'product',
            '_time',
            'price',
            'salesrank'
        )


class SalesRankHistoryByDaySerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesRankHistoryByDay
        fields = (
            'product',
            '_time',
            'price',
            'salesrank'
        )
