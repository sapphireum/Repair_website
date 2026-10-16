from django.db import models
from datetime import date

# Client
class Clients(models.Model):
    name = models.CharField(max_length=60, unique=True, verbose_name="ФИО")
    phone = models.CharField(max_length=12, verbose_name="Телефон")
    email = models.CharField(max_length=320, verbose_name="Почта")
    
    created_date = models.DateField(default=date.today, verbose_name="Дата создания")
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")

    class Meta:
        db_table = "client"
        verbose_name = "Клиента"
        verbose_name_plural = "Клиента"

    def __str__(self):
        return self.name
    
    def extid(self):
        return f"{self.id:08d}"


# Master
class Masters(models.Model):
    name = models.CharField(max_length=60, unique=True, verbose_name="ФИО")
    phone = models.CharField(max_length=12, verbose_name="Телефон")
    email = models.CharField(max_length=320, verbose_name="Почта")
    address = models.CharField(max_length=50, verbose_name="Адрес")
    
    created_date = models.DateField(default=date.today, verbose_name="Дата создания")
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")

    class Meta:
        db_table = "master"
        verbose_name = "Мастера"
        verbose_name_plural = "Мастера"

    def __str__(self):
        return self.name
    
    def extid(self):
        return f"{self.id:08d}"


# TypeIssue
class TypeIssues(models.Model):
    name = models.CharField(max_length=60, unique=True, verbose_name="Наименование")

    is_deleted = models.BooleanField(default=False, verbose_name="Удален")
    
    class Meta:
        db_table = "typeissue"
        verbose_name = "Тип проблемы"
        verbose_name_plural = "Типа проблемы"

    def __str__(self):
        return self.name
    
    def extid(self):
        return f"{self.id:08d}"


# StatusOrder
class StatusOrders(models.Model):
    name = models.CharField(max_length=60, unique=True, verbose_name="Наименование")
    
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")

    class Meta:
        db_table = "statusorder"
        verbose_name = "Статус заявки"
        verbose_name_plural = "Статуса заявки"

    def __str__(self):
        return self.name
    
    def extid(self):
        return f"{self.id:08d}"


# Orders
class Orders(models.Model):  # Добавить мастера (Master)
    comment_prob = models.CharField(max_length=500)

    client = models.ForeignKey(
        to=Clients, on_delete=models.PROTECT, verbose_name="Клиент"
    )
    # Master
    master = models.ForeignKey(
        to=Masters, on_delete=models.PROTECT, verbose_name="Мастер"
    )

    type_issue = models.ForeignKey(
        to=TypeIssues, on_delete=models.PROTECT, verbose_name="Тип проблемы"
    )

    status_order = models.ForeignKey(
        to=StatusOrders, on_delete=models.PROTECT, verbose_name="Статус заявки"
    )

    price = models.DecimalField(
        default=0.00, max_digits=7, decimal_places=2, verbose_name="Цена"
    )
    
    idTech = models.CharField(max_length=128, blank=True, verbose_name="Код техники")
    
    created_date = models.DateField(default=date.today, verbose_name="Дата создания")
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")

    class Meta:
        db_table = "order"
        verbose_name = "Заявку"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return f"[{self.pk}] Заявка:  Клиент-{self.client.name}"
    
    def extid(self):
        return f"{self.id:08d}"
