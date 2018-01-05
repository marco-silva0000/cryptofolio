
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.utils import timezone


class Coin(models.Model):
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=16)

    def __str__(self):
        return '%s - %s' % (self.code, self.name)


class Exchange(models.Model):
    name = models.CharField(max_length=64)
    url = models.URLField(max_length=64)

    def __str__(self):
        return '%s' % self.name


class Account(models.Model):
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    _value = models.DecimalField(max_digits=19, decimal_places=10)
    latest_reconcile_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '%s - %s' % (self.coin, self._value)

    def widraw(self, value, **kwargs):
        self._value -= value
        self.latest_reconcile_date = timezone.now()
        self.save()

    def deposit(self, value, **kwargs):
        self._value += value
        self.latest_reconcile_date = timezone.now()
        self.save()


class Transaction(models.Model):
    _initial_value = models.DecimalField(max_digits=19, decimal_places=10, null=True, blank=True)
    price_value = models.DecimalField(max_digits=19, decimal_places=10, null=True, blank=True)
    final_value = models.DecimalField(max_digits=19, decimal_places=10)
    original_account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.CASCADE,
                                         related_name='original')
    destination_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='destination')

    def __str__(self):
        return '%s to %s' % (self.final_value, self.destination_account)

    @property
    def initial_value(self):
        if self._initial_value:
            return self._initial_value
        return self.final_value


def process_transaction(instance, **kwargs):
    if instance.original_account:
        instance.original_account.widraw(instance.initial_value)
    instance.destination_account.deposit(instance.final_value)

models.signals.post_save.connect(process_transaction, Transaction)

