from django.contrib import admin

# Register your models here.
from .models import Productos
from .models import Pedidos

# Register your models here.
admin.site.register(Productos)
admin.site.register(Pedidos)
