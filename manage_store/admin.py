import time

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
import io
import zipfile

from manage_groha_store.settings import MY_LOGGER
from manage_store.models import ProductFiles, Category, ProjectSettings


@admin.action(description='скачать файлы')
def download_files(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    """
    Скачать файлы
    """
    MY_LOGGER.info(f'Вызван экшн для скачивания файлов')

    # Создаём буфер для хранения ZIP архива
    zip_buffer = io.BytesIO()

    # Создаём ZIP архив
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for i_obj in queryset:
            # Добавим файл в ZIP архив с использованием его оригинального имени
            zip_file.write(filename=i_obj.file.path, arcname=i_obj.file.name)

    # Установим указатель чтения в начало буфера
    zip_buffer.seek(0)

    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="files.zip"'
    return response


@admin.action(description='скачать и удалить файлы')
def download_and_delete_files(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    """
    Скачать и удалить файлы.
    """
    MY_LOGGER.info(f'Вызван экшн для скачивания и удаления файлов')

    # Достаём из БД ключ настройки admin_time_to_del
    try:
        time_to_del = float(ProjectSettings.objects.get(key='admin_time_to_del').value)
    except ObjectDoesNotExist as err:
        MY_LOGGER.debug(f'Ключ admin_time_to_del не установлен в настройках проекта. Используем значение 120 мин.\n'
                        f'Текст исключения: {err}')
        time_to_del = 120

    # Создаём буфер для хранения ZIP архива
    zip_buffer = io.BytesIO()

    # Создаём ZIP архив
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for i_obj in queryset:
            # Добавим файл в ZIP архив с использованием его оригинального имени
            zip_file.write(filename=i_obj.file.path, arcname=i_obj.file.name)
            i_obj.time_for_delete = time.time() + time_to_del   # Установим время для удаления
            i_obj.is_sold = True    # Флаг, что товар(файл) продан позволит его удалить
            i_obj.save()

    # Установим указатель чтения в начало буфера
    zip_buffer.seek(0)

    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="files.zip"'
    return response


@admin.register(ProductFiles)
class ProductFilesAdmin(admin.ModelAdmin):
    actions = [
        download_files,
        download_and_delete_files,
    ]
    list_display = [
        'id',
        'is_sold',
        'is_links_list',
        'when_delete',
        'category',
        'download_link',
        'origin_file_name',
    ]
    list_display_links = [
        'id',
        'is_sold',
        'is_links_list',
        'when_delete',
        'category',
        'download_link',
        'origin_file_name',
    ]
    list_filter = [
        'is_sold',
        'is_links_list',
        'category',
    ]
    search_fields = [
        'id',
        'is_sold',
        'is_links_list',
        'category',
        'download_link',
        'origin_file_name',
        'when_delete'
    ]
    search_help_text = 'Поиск по полям, указанным в таблице'


''' НАСТРОЙКИ АДМИНКИ ДЛЯ МОДЕЛИ Category '''


@admin.action(description='скачать файлы из папки')
def download_category_files(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    """
    Скачать файлы конкретной категории.
    """
    MY_LOGGER.info(f'Вызван экшн для скачивания файлов категории')

    # Создаём буфер для хранения ZIP архива
    zip_buffer = io.BytesIO()

    # Создаём ZIP архив
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for i_cat in queryset:  # итерируемся по категориям
            prod_files = ProductFiles.objects.filter(category=i_cat)

            for i_obj in prod_files:    # Итерируемся по объектам файлов категории
                # Добавим файл в ZIP архив с использованием его оригинального имени
                zip_file.write(filename=i_obj.file.path, arcname=i_obj.file.name)

    # Установим указатель чтения в начало буфера
    zip_buffer.seek(0)

    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="files.zip"'
    return response


@admin.action(description='скачать и удалить файлы из папки')
def download_and_delete_category_files(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    """
    Скачать и удалить файлы конкретной категории.
    """
    MY_LOGGER.info(f'Вызван экшн для скачивания и удаления файлов категории')

    # Достаём из БД ключ настройки admin_time_to_del
    try:
        time_to_del = float(ProjectSettings.objects.get(key='admin_time_to_del').value)
    except ObjectDoesNotExist as err:
        MY_LOGGER.debug(f'Ключ admin_time_to_del не установлен в настройках проекта. Используем значение 120 мин.\n'
                        f'Текст исключения: {err}')
        time_to_del = 120

    # Создаём буфер для хранения ZIP архива
    zip_buffer = io.BytesIO()

    # Создаём ZIP архив
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for i_cat in queryset:  # Итерируемся по категориям
            prod_files = ProductFiles.objects.filter(category=i_cat)

            for i_obj in prod_files:  # Итерируемся по объектам файлов категории
                # Добавим файл в ZIP архив с использованием его оригинального имени
                zip_file.write(filename=i_obj.file.path, arcname=i_obj.file.name)
                i_obj.time_for_delete = time.time() + time_to_del   # Установим время для удаления
                i_obj.is_sold = True  # Флаг, что товар(файл) продан позволит его удалить
                i_obj.save()

    # Установим указатель чтения в начало буфера
    zip_buffer.seek(0)

    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="files.zip"'
    return response


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    actions = [
        download_category_files,
        download_and_delete_category_files,
    ]
    list_display = [
        'id',
        'cat_name',
        'created_at',
    ]
    list_display_links = [
        'id',
        'cat_name',
        'created_at',
    ]


@admin.register(ProjectSettings)
class ProjectSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'key',
    ]
    list_display_links = [
        'id',
        'key',
    ]
