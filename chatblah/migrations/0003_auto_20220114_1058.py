# Generated by Django 3.2.10 on 2022-01-14 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatblah', '0002_pedidos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pedidos',
            name='sesion',
        ),
        migrations.AddField(
            model_name='pedidos',
            name='objeto',
            field=models.CharField(default='producto no especificado', max_length=30),
            preserve_default=False,
        ),
    ]
