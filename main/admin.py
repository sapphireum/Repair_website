from django.contrib import admin
from main.models import TypeIssues, StatusOrders, Orders, Clients, Masters

# Register your models here.
admin.site.register(TypeIssues)
admin.site.register(StatusOrders)
admin.site.register(Orders)
admin.site.register(Clients)
admin.site.register(Masters)
