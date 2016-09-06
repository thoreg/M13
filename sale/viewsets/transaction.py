from rest_framework import viewsets

from ..models import Transaction
from ..serializers import TransactionSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('-_time')
    serializer_class = TransactionSerializer
