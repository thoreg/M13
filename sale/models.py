
from django.db import models


class Transaction(models.Model):
    _time = models.DateTimeField()
    _type = models.CharField(max_length=64)
    order_id = models.CharField(
        max_length=32,
        blank=True,
        null=True)
    sku = models.CharField(
        max_length=32,
        blank=True,
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
        max_length=32,
        primary_key=True)
    asin = models.CharField(max_length=32)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    depth = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=32, blank=True, null=True)
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
