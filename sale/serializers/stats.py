from rest_framework import serializers


class TransactionDayStatsSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    year = serializers.CharField(max_length=256)
    month = serializers.CharField(max_length=256)
    day = serializers.CharField(max_length=256)
    sum_total = serializers.CharField(max_length=256)
