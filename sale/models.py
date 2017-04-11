from pprint import pprint
from django.core.exceptions import ValidationError
from datetime import date

from django.db import models
from django.db.models import Avg


class Transaction(models.Model):
    _time = models.DateTimeField()
    _type = models.CharField(max_length=64)
    order_id = models.CharField(
        max_length=32,
        blank=True,
        null=True)
    product = models.ForeignKey(
        'Product',
        blank='',
        null=True)
    amount = models.PositiveSmallIntegerField(
        blank=True,
        null=True)
    marketplace = models.CharField(
        max_length=64,
        blank=True,
        null=True)
    dispatch_type = models.CharField(
        max_length=32,
        blank=True,
        null=True)
    city = models.CharField(
        max_length=64,
        blank=True,
        null=True)
    postal_code = models.CharField(
        max_length=16,
        blank=True,
        null=True)
    turnover = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Umsatz')
    voucher_shipping_costs = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Gutschrift für Versandkosten')
    charge = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Verkaufsgebühren')
    charge_fba = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Gebühren zu Versand durch Amazon')
    charge_other = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Andere Transaktionsgebühren')
    other = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Andere')
    total = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        help_text='Gesamt')

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return self.order_id


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=512)
    sku = models.CharField(
        max_length=64,
        primary_key=True)
    asin = models.CharField(max_length=32)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    depth = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=64, blank=True, null=True)
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING)
    subcategory = models.OneToOneField(
        SubCategory,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING)

    def __str__(self):
        return '{} - {}'.format(self.sku, self.name)

    def avg_salesrank_last_seven_days(self):
        """
        Take the salesranks of the last 8 days and return the average salesrank
        of the last 7 days and the value of the average of the last seven days
        from yesterday and a tendence indicator if things getting better or worse.

        """
        salesranks = SalesRankHistoryByDay.objects.filter(product=self) \
                                                  .order_by('-_time')   \
                                                  .values()[:8]

        # Trigger queryset here - otherwise django performs two queries
        for s in salesranks:
            pass

        last_seven_days = salesranks[:7]
        before_last_seven_days = salesranks[1:]

        salesrank_before = 0
        for b in before_last_seven_days:
            salesrank_before += b['salesrank']
        avg_salesrank_before = salesrank_before / len(before_last_seven_days)

        salesrank_last_seven_days = 0
        for s in last_seven_days:
            salesrank_last_seven_days += s['salesrank']
        avg_salesrank_last_seven_days = salesrank_last_seven_days / len(last_seven_days)

        return {
            'avg_salesrank_before': int(avg_salesrank_before),
            'avg_salesrank_last_seven_days': int(avg_salesrank_last_seven_days),
            'better': int(avg_salesrank_before) > int(avg_salesrank_last_seven_days)
        }


class ProductDescriptionDE(models.Model):
    product = models.OneToOneField(Product, primary_key=True)
    description = models.CharField(max_length=16384)

    def __str__(self):
        return self.product


class BaseSalesRankHistory(models.Model):
    product = models.ForeignKey(Product)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2)
    salesrank = models.IntegerField()

    class Meta:
        abstract = True


class SalesRankHistory(BaseSalesRankHistory):
    _time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} {} {}'.format(self.product, self.salesrank, self.price)


class SalesRankHistoryByDay(BaseSalesRankHistory):
    _time = models.DateTimeField()

    def __str__(self):
        return '[ by_day ] {} {} {} {}'.format(
            self.product.name[:20],
            self._time,
            self.salesrank,
            self.price)


class TransactionsByDay(models.Model):
    category = models.ForeignKey('Category')
    _time = models.DateField()
    turnover = models.DecimalField(
        max_digits=12,
        decimal_places=2)


class ProductMarker(models.Model):
    """
    Mark/describe special events applied/related to the specific product.

    """
    product = models.ForeignKey(Product)
    category = models.ForeignKey(Category)
    description = models.CharField(max_length=2048)
    action_date = models.DateField(default=date.today)
    global_event = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.name[:10] + ' ' + self.description[:42]

    @property
    def product_short_description(self):
        return self.product.sku + ' ' + self.product.name[:24]
