
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from sale.views import IndexView, ProductDetailView
from sale.viewsets import (SalesRankHistoryByDayList, SalesRankHistoryList,
                           TransactionDayStatsList, TransactionList, TransactionsByDayList, ProductMarkerList)

urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^api/salesrankhistories-by-day/', SalesRankHistoryByDayList.as_view()),
    url(r'^api/salesrankhistories/', SalesRankHistoryList.as_view()),
    url(r'^api/productmarkers/', ProductMarkerList.as_view()),

    url(r'^api/stats/', TransactionDayStatsList.as_view()),
    url(r'^api/transactions/', TransactionList.as_view()),
    url(r'^api/transactions-by-day/',
        TransactionsByDayList.as_view(),
        name="transactions-by-day"),

    url(r'^maddt/', admin.site.urls),

    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}),
    # url(r'^logout/$', auth_views.logout, name='logout'),


    url(r'^product/(?P<sku>.*)/$', ProductDetailView.as_view(), name='product-detail'),
    url(r'^$', IndexView.as_view(), name="index"),
]
