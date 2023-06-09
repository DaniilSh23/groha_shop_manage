# Generated by Django 4.2 on 2023-04-23 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manage_store', '0005_productfiles_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=350, verbose_name='ключ настройки')),
                ('value', models.TextField(max_length=5000, verbose_name='значение настройки')),
            ],
            options={
                'verbose_name': 'настройка',
                'verbose_name_plural': 'настройки',
                'ordering': ['-id'],
            },
        ),
    ]
