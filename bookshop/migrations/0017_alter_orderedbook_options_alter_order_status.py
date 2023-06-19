# Generated by Django 4.2.1 on 2023-06-16 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookshop', '0016_alter_deliveryaddress_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderedbook',
            options={'ordering': ('-order',), 'verbose_name': 'Заказанная книга', 'verbose_name_plural': 'Заказанные книги'},
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('В работе', 'В работе'), ('Передан в службу доставки', 'Передан в службу доставки'), ('Доставлен', 'Доставлен'), ('Отменен', 'Отменен')], default='В работе', verbose_name='Статус заказа'),
        ),
    ]
