import logging
import time
from collections import OrderedDict
from datetime import datetime, timedelta
from decimal import Decimal
from pprint import pprint

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from .models import Category, Product, SalesRankHistory, SalesRankHistoryByDay, TransactionsByDay

log = logging.getLogger('sale')


class IndexView(TemplateView):
    template_name = 'sale/index.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all().values('name').order_by('name')

        return context


class ProductDetailView(TemplateView):
    template_name = 'sale/product.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProductDetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        sku = context.get('sku')
        if not sku:
            context['error'] = "Kein Produkt gefunden"
            return context

        product = Product.objects.get(sku=sku)
        context['product'] = product
        context['avg'] = product.avg_salesrank_last_seven_days()

        return context
