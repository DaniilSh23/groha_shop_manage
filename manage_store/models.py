import datetime
import os.path
import random
import string
import time

from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import hashlib

from django.urls import reverse

from manage_groha_store.settings import DOMAIN_NAME


class Category(models.Model):
    """
    Модель категорий, для Димана - это папки.
    """
    cat_name = models.CharField(verbose_name='Папка', max_length=100)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'папка'
        verbose_name_plural = 'папки'

    def __str__(self):
        return self.cat_name


class ProductFiles(models.Model):
    """
    Файлы цифровых товаров.
    """
    origin_file_name = models.CharField(verbose_name='исходное имя файла', max_length=300)
    file_hash = models.CharField(verbose_name='хэш файла', max_length=300, blank=True, null=False)
    download_link = models.URLField(verbose_name='ссылка для скачивания', max_length=1000, blank=True, null=False)
    is_sold = models.BooleanField(verbose_name='Продано', default=False)
    is_links_list = models.BooleanField(verbose_name='Список ссылок', default=False)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    time_for_delete = models.CharField(verbose_name='Время удаления', max_length=50, blank=True, null=False)
    file = models.FileField(verbose_name='Файл', upload_to='product_files')
    category = models.ForeignKey(verbose_name='Папка', to=Category, on_delete=models.CASCADE)

    @property
    def when_delete(self):
        """
        Метод для форматирования секунд в дату и время.
        """
        if self.time_for_delete:
            dt = datetime.datetime.fromtimestamp(float(self.time_for_delete))
            formatted_time = dt.strftime('%d.%m.%Y %H:%M:%S')
            return formatted_time
        else:
            return 'не установлено'

    def save(self, *args, **kwargs):
        """
        Переопределяем метод save() для заполнени полей file_hash и download_link, если они пустые.
        """
        if not self.file_hash:  # Если хэш не указан
            base_string = f'{self.origin_file_name}:{time.time()}:{random.choices(string.ascii_letters, k=8)}'
            hash_object = hashlib.md5(base_string.encode('utf-8'))  # Создаём объект хэша
            md5_hash = hash_object.hexdigest()  # Получаем хэш в виде строки
            self.file_hash = md5_hash

        if not self.download_link:  # Если ссылка на скачивание не указана
            self.download_link = f'{DOMAIN_NAME}{reverse("manage_store:dwnld", args=[self.file_hash])}'
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'файл товара'
        verbose_name_plural = 'файлы товаров'


@receiver(pre_delete, sender=ProductFiles)
def delete_file_before_delete_instance(sender, instance, **kwargs):
    """
    Удаление файла перед удалением инстанса модели.
    """
    if instance.file and os.path.exists(instance.file.path):
        os.remove(instance.file.path)


class ProjectSettings(models.Model):
    """
    Модель для различных настроек. Просто key-value хранилище.
    """
    key = models.CharField(verbose_name='ключ настройки', max_length=350)
    value = models.TextField(verbose_name='значение настройки', max_length=5000)

    class Meta:
        verbose_name = 'настройка'
        verbose_name_plural = 'настройки'
        ordering = ['-id']
