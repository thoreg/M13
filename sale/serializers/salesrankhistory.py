from rest_framework import serializers

from ..models import Product, ProductMarker, SalesRankHistory, SalesRankHistoryByDay


class SalesRankHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesRankHistory
        fields = (
            'product',
            '_time',
            'price',
            'salesrank'
        )


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'name',
            'sku',
            'asin',
        )


class ProductMarkerSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductMarker
        fields = (
            'product',
            'description',
            'action_date',
        )


class SalesRankHistoryByDaySerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesRankHistoryByDay
        fields = (
            'product',
            '_time',
            'price',
            'salesrank',
        )
