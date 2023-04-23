# Generated by Django 4.2 on 2023-04-21 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manage_store', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productfiles',
            name='new_file_name',
        ),
        migrations.AddField(
            model_name='productfiles',
            name='file_hash',
            field=models.CharField(blank=True, max_length=300, verbose_name='хэш файла'),
        ),
    ]
