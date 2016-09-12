
from django.conf.urls import include, url
from django.contrib import admin

from sale.viewsets import TransactionList, TransactionDayStatsList
from sale.views import index

urlpatterns = [
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),

    url(r'^api/stats/', TransactionDayStatsList.as_view()),
    url(r'^api/transactions/', TransactionList.as_view()),

    url(r'^addi/', admin.site.urls),
    url(r'^$', index),
]
