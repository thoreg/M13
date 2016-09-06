
from django.conf.urls import include, url
from django.contrib import admin

from sale.viewsets import TransactionList


urlpatterns = [
    url(r'^api/transactions/', TransactionList.as_view()),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),

    url(r'^admin/', admin.site.urls),
]
