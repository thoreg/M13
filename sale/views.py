import logging
import time
from collections import OrderedDict
from decimal import Decimal


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from .models import Product, SalesRankHistory, SalesRankHistoryByDay

log = logging.getLogger('sale')

to_js_date = lambda date_: int(time.mktime(date_.timetuple()) * 1000)


def index(request):
    context = {}

    return render(request, 'sale/index.html', context)


class ProductDetailView(TemplateView):
    template_name = 'sale/product.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProductDetailView, self).dispatch(*args, **kwargs)

    def get_price_and_salesrank_history_charts(self, history_entries, suffix):
        charts = []
        xdata = []
        result = OrderedDict()
        date_format = '%Y-%m-%d'
        extra_y = {
            'tooltip': {
                'y_start': 'There are ',
                'y_end': ' calls'
            },
        }

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
