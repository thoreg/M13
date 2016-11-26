from datetime import datetime

from rest_framework import generics, viewsets

from ..models import SalesRankHistory, SalesRankHistoryByDay
from ..serializers import SalesRankHistoryByDaySerializer, SalesRankHistorySerializer


class SalesRankHistoryList(generics.ListAPIView):
    serializer_class = SalesRankHistorySerializer

    def get_queryset(self):
        queryset = SalesRankHistory.objects.all()

        sku = self.request.query_params.get('sku', None)
        if sku is not None:
            queryset = queryset.filter(product__sku=sku).order_by('_time')

        return queryset


class SalesRankHistoryByDayList(generics.ListAPIView):
    serializer_class = SalesRankHistoryByDaySerializer

    def get_queryset(self):
        queryset = SalesRankHistoryByDay.objects.all()

        sku = self.request.query_params.get('sku', None)
        if sku is not None:
            queryset = queryset.filter(product__sku=sku).order_by('_time')

        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        if from_date and to_date:
            from_date = datetime.strptime(from_date, '%m-%d-%Y')
            to_date = datetime.strptime(to_date, '%m-%d-%Y')
            queryset = queryset.filter(_time__range=[from_date, to_date]) \
                               .order_by('_time')

        return queryset
