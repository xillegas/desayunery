from django.db import models

# Create your models here.
class Productos(models.Model):
	nombre=models.CharField(max_length=20)
	descripcion=models.CharField(max_length=120)
	precio=models.PositiveIntegerField()

class Pedidos(models.Model):
	objeto=models.CharField(max_length=30)
	cantidad=models.PositiveIntegerField()
	email=models.EmailField()
	telefono=models.CharField(max_length=16)
	direccion=models.CharField(max_length=150)

class Sesiones(models.Model):
	identificador=models.CharField(max_length=40)
