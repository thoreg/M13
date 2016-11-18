from rest_framework import generics, viewsets

from ..models import Product, Transaction, TransactionsByDay
from ..serializers import TransactionsByDaySerializer, TransactionSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('-_time')
    serializer_class = TransactionSerializer


class TransactionList(generics.ListAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        queryset = Transaction.objects.all().exclude(sku__isnull=True)

        year = self.request.query_params.get('year', None)
        if year is not None:
            queryset = queryset.filter(_time__year=year)

        month = self.request.query_params.get('month', None)
        if month is not None:
            queryset = queryset.filter(_time__month=month)

        day = self.request.query_params.get('day', None)
        if day is not None:
            queryset = queryset.filter(_time__day=day)

        category = self.request.query_params.get('category', None)
        if category is not None:
            list_of_skus = Product.objects.filter(category__name=category) \
                                          .values_list('sku', flat=True)
            queryset = queryset.filter(sku__in=list_of_skus)

        sku = self.request.query_params.get('sku', None)
        if sku is not None:
            queryset = queryset.filter(sku=sku)

        return queryset


class TransactionsByDayList(generics.ListAPIView):
    serializer_class = TransactionsByDaySerializer

    def get_queryset(self):
        queryset = TransactionsByDay.objects.all()

        year = self.request.query_params.get('year', None)
        if year is not None:
            queryset = queryset.filter(_time__year=year)

        month = self.request.query_params.get('month', None)
        if month is not None:
            queryset = queryset.filter(_time__month=month)

        day = self.request.query_params.get('day', None)
        if day is not None:
            queryset = queryset.filter(_time__day=day)

        category = self.request.query_params.get('category', None)
        if category is not None:
            queryset = queryset.filter(category__name=category)

        return queryset
