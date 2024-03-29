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
from manage_store.utils import extract_domain, update_file_with_links_list


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
        Переопределяем метод save() для заполнения полей file_hash и download_link, если они пустые.
        """
        if not self.file_hash:  # Если хэш не указан
            base_string = f'{self.origin_file_name}:{time.time()}:{random.choices(string.ascii_letters, k=8)}'
            hash_object = hashlib.md5(base_string.encode('utf-8'))  # Создаём объект хэша
            md5_hash = hash_object.hexdigest()  # Получаем хэш в виде строки
            self.file_hash = md5_hash

        if not self.download_link:  # Если ссылка на скачивание не указана
            domain_name = ProjectSettings.objects.get(key='download_domain').value
            self.download_link = f'{domain_name}{reverse("manage_store:dwnld", args=[self.file_hash])}'
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

    def save(self, *args, **kwargs):
        """
        Переопределяем метод save для дополнения логики, которая выполняется при сохранении записи в БД.
        """
        # Изменяем домен в ссылках на скачивание
        if self.key == 'download_domain':
            files = ProductFiles.objects.all().only('download_link', 'is_links_list', 'file')
            for i_file in files:
                old_domain = extract_domain(url=i_file.download_link)
                i_file.download_link = i_file.download_link.replace(old_domain, self.value)
                i_file.save()

                # Если итерируемый файл является список ссылок
                if i_file.is_links_list:
                    update_file_with_links_list(file_path=i_file.file.path, new_domain=self.value)
        super().save(*args, **kwargs)

