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

to_js_date = lambda date_: int(time.mktime(date_.timetuple()) * 1000)


class IndexView(TemplateView):
    template_name = 'sale/index.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all().values('name')

        return context


class NOTACTIVEIndexView(TemplateView):
    template_name = 'sale/index.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NOTACTIVEIndexView, self).dispatch(*args, **kwargs)

    def get_buckets_turnover_by_category(self, year):
        """
        Group all the data per category.

        """
        begin = datetime.strptime(year, '%Y')
        end = begin + timedelta(days=30)
        print('\nBegin: {} End: {}\n'.format(begin, end))
        transactions = TransactionsByDay.objects.select_related('category') \
                                                .filter(_time__range=[begin, end])

        turnover = transactions.values_list('category__name', 'turnover', '_time')
        buckets = {}
        for category, value, _time in turnover:
            if category not in buckets:
                buckets[category] = []
            buckets[category].append((_time, value))

        return buckets

    def get_turnover_by_category_chart(self):
        buckets = self.get_buckets_turnover_by_category('2016')
        chartdata = {}
        xdata = []
        extra_serie = {"tooltip": {"y_start": "There are ", "y_end": " calls"}}

        print("Number of categories: {}".format(len(buckets)))

        for idx, (category, values) in enumerate(buckets.items()):
            # print(category, values)
            idx += 1
            ydata = []
            for _time, turnover_sum in values:

                if len(values) > len(xdata):
                    for _time, _not_used in values:
                        _date = to_js_date(_time)
                        if _date not in xdata:
                            xdata.append(_date)

                if isinstance(turnover_sum, Decimal):
                    turnover_sum = float('{}'.format(turnover_sum))
                ydata.append(turnover_sum)

            chartdata.update({
                'name{}'.format(idx): '{}'.format(category),
                'y{}'.format(idx): ydata,
                'extra{}'.format(idx): extra_serie,
            })

        chartdata['x'] = sorted(xdata)
        chart = {
            'charttype': "multiBarChart",
            'chartdata': chartdata,
            'container_name': 'turnover',
            'extra': {
                'x_is_date': True,
                'x_axis_format': '%Y-%m-%d',
                'color_category': 'category20',
            }
        }

        return chart

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['turnover_by_category'] = self.get_turnover_by_category_chart()
        pprint(context)
        # import ipdb; ipdb.set_trace()
        return context


class ProductDetailView(TemplateView):
    template_name = 'sale/product.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProductDetailView, self).dispatch(*args, **kwargs)

    def get_price_and_salesrank_history_charts(self, history_entries, suffix):
        DATE_FORMATS = {
            'by_day': '%Y-%m-%d',
            'plain': '%Y-%m-%d %H'
        }

        charts = []
        xdata = []

        date_format = DATE_FORMATS[suffix]

        extra_y = {
            'tooltip': {
                'y_start': 'There are ',
                'y_end': ' calls'
            },
        }

        result = OrderedDict()
        for entry in history_entries:
            try:
                result['salesrank'].append((entry['_time'], entry['salesrank']))
            except KeyError:
                result['salesrank'] = []

            try:
                result['price'].append((entry['_time'], entry['price']))
            except KeyError:
                result['price'] = []

        for index_chart, (category, values) in enumerate(result.items()):
            for _time, value in values:
                ydata = []
                index_chart += 1
                for _time, value in values:
                    if isinstance(value, Decimal):
                        value = float('{}'.format(value))
                    ydata.append(value)
                    if index_chart == 1:
                        xdata.append(to_js_date(_time))

                chartdata = {
                    'extra{}'.format(index_chart): extra_y,
                    'x': xdata,
                    'y{}'.format(index_chart): ydata,
                }

            charts.append({
                'category': category.capitalize(),
                'chartdata': chartdata,
                'charttype': "lineWithFocusChart",
                'container_name': 'salesrank_{}_{}'.format(index_chart, suffix),
                'extra': {
                    'x_is_date': True,
                    'x_axis_format': date_format,
                    'color_category': 'category20'
                }
            })

        return charts

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        sku = context.get('sku')
        if not sku:
            context['error'] = "Kein Produkt gefunden"
            return context

        product = Product.objects.get(sku=sku)
        context['product'] = product

        history_entries_by_day = SalesRankHistoryByDay.objects.filter(product=product).values()
        context['charts_by_day'] = self.get_price_and_salesrank_history_charts(history_entries_by_day, 'by_day')

        history_entries_plain = SalesRankHistory.objects.filter(product=product).values()
        context['charts_plain'] = self.get_price_and_salesrank_history_charts(history_entries_plain, 'plain')

        return context
