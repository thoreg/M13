
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers
from sale.viewsets import TransactionViewSet


router = routers.DefaultRouter()
router.register(r'transactions', TransactionViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),

    url(r'^admin/', admin.site.urls),
]
