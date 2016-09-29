from rest_framework import serializers

from ..models import SalesRankHistory


class SalesRankHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesRankHistory
        fields = (
            'product',
            '_time',
            'price',
            'sales_rank'
        )
