
from django.conf.urls import include, url
from django.contrib import admin

from sale.views import index, ProductDetailView
from sale.viewsets import (SalesRankHistoryList, TransactionDayStatsList,
                           TransactionList)

urlpatterns = [
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),

    url(r'^api/stats/', TransactionDayStatsList.as_view()),
    url(r'^api/transactions/', TransactionList.as_view()),

    url(r'^api/salesrankhistories/', SalesRankHistoryList.as_view()),

    url(r'^addi/', admin.site.urls),

    url(r'^product/(?P<sku>.*)/$',
        ProductDetailView.as_view(),
        name='product-detail'),
    url(r'^$', index),
]
