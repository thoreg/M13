
import collections
from sale.models import Product


def products(request):
    """ Used in main navigation """
    product_title_by_category = {}
    for product in Product.objects \
            .exclude(salesrankhistorybyday__product__isnull=True) \
            .values('category__name', 'sku', 'name'):

        category = product['category__name']

        if category not in product_title_by_category:
            product_title_by_category[category] = []

        product_title_by_category[category].append(
            (product['sku'], product['name'][:55]))

    for category, products in product_title_by_category.items():
        product_title_by_category[category] = sorted(products)

    return {'skus_with_salesrank_info_by_category': collections.OrderedDict(
        sorted(product_title_by_category.items(), key=lambda t: t[0]))}
