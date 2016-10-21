
from sale.models import Product


def products(request):
    """ Used in main navigation """
    skus_by_category = {}
    for product in Product.objects.exclude(salesrankhistorybyday__product__isnull=True) \
                                  .values('category__name', 'sku'):
        category = product['category__name']
        if category not in skus_by_category:
            skus_by_category[category] = []
        skus_by_category[category].append(product['sku'])

    return {'skus_with_salesrank_info_by_category': skus_by_category}
