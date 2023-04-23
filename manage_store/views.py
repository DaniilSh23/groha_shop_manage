import datetime
import time
from urllib.parse import quote

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from loguru import logger

from django.http import FileResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from manage_groha_store.settings import MEDIA_ROOT
from manage_store.forms import UploadProductFilesForm, AddCategoryForm
from manage_store.models import ProductFiles, Category, ProjectSettings


class DownloadProductFileView(View):
    """
    Вьюшка для скачивания файла - цифрового товара.
    """

    def get(self, request, file_hash, format=None):
        """
        Скачивание файла.
        """
        # Находим файл в БД
        prod_file_obj = get_object_or_404(klass=ProductFiles, file_hash=file_hash)

        # Устанавливаем ему время удаления
        try:
            time_to_delete = int(ProjectSettings.objects.get(key='time_to_delete').value) * 60
        except Exception as error:
            logger.warning(f'Не найдено значение по ключу настройки time_to_delete, будет использовано 32 часа.\n'
                           f'Ошибка:\n{error}')
            time_to_delete = 32 * 60 * 60

        prod_file_obj.time_for_delete = time.time() + time_to_delete
        prod_file_obj.is_sold = True
        prod_file_obj.save()

        download_file = open(prod_file_obj.file.path, 'rb')
        response = FileResponse(download_file)
        response['content-disposition'] = f'attachment; filename={quote(prod_file_obj.origin_file_name)}'
        return response


class UploadProductFilesView(View):
    """
    Вьюшка для отрисовки страницы загрузки файлов-цифровых товаров.
    """
    def get(self, request):
        """
        Отдаём страничку с формой для загрузки цифровых товаров.
        """
        # Редирект, если незалогинен
        if not request.user.is_superuser or not request.user.is_staff:
            return redirect(to=reverse_lazy('manage_store:login'))

        context = {
            'file_form': UploadProductFilesForm(),
            'category_form': AddCategoryForm(),
        }
        return render(request=request, template_name='manage_store/upload_files.html', context=context)

    def post(self, request):
        """
        Вьюшка для получения файлов.
        """
        # Редирект, если незалогинен
        if not request.user.is_superuser or not request.user.is_staff:
            return redirect(to=reverse_lazy('manage_store:login'))

        file_form = UploadProductFilesForm(request.POST, request.FILES)

        if file_form.is_valid():
            # Если папка не была выбрана
            if file_form.cleaned_data.get("category") == '0':
                context = {
                    'file_form': file_form.add_error(field='category', error='Сперва нужно создать папку'),
                    'category_form': AddCategoryForm(),
                }
                return HttpResponse(status=400, content='☝️Ошибка. Сперва нужно создать папку📁')

            # Получаем нужную папку
            try:
                cat_obj = Category.objects.get(pk=file_form.cleaned_data.get("category"))
            except Exception as error:
                logger.warning(f'При сохранении файлов не найдена папка. Ошибка: {error}\nЗапрос:{request.POST}')
                context = {
                    'file_form': file_form.add_error(field='category', error='Такой папки нет.'),
                    'category_form': AddCategoryForm(),
                }
                return render(request=request, template_name='manage_store/upload_files.html', context=context)

            dwnld_links_lst = []    # Список для ссылок на скачивание файлов [(origin_file_name, download_link)]
            for i_file in request.FILES.getlist('files'):
                try:
                    # Сохраняем файлы товаров
                    i_prod_file_obj = ProductFiles.objects.create(
                        origin_file_name=i_file.name,
                        file=i_file,
                        category=cat_obj,
                    )
                    logger.success(f'Файл {i_file.name} сохранён.')
                    # Добавляем имя файла и ссылку в общий список
                    dwnld_links_lst.append((i_prod_file_obj.origin_file_name, i_prod_file_obj.download_link))
                except Exception as error:
                    logger.warning(f'Файл {i_file.name} не сохранён! Текст ошибки:\n{error}')

            # Записываем ссылки в отдельный файл
            links_lst_path = f'{MEDIA_ROOT}/work_files/links_lst{datetime.datetime.now().strftime("%d.%m.%Y_%H:%M:%S")}'
            with open(links_lst_path, 'w', encoding='utf-8') as links_file:
                for i_link in dwnld_links_lst:
                    links_file.write(f'{i_link[1]}\n')

            # "Сохраняем файл" со списком ссылок в БД
            cat_obj = Category.objects.get_or_create(    # Создаём или достаём папку для списков ссылок
                    cat_name='файлы со списком ссылок',
                    defaults={
                        "cat_name": "файлы со списком ссылок",
                    }
                )[0]
            links_file_obj = ProductFiles.objects.create(
                origin_file_name=links_lst_path.split('/')[-1],
                file=links_lst_path,
                is_links_list=True,
                category=cat_obj,
            )

            # Даём ответ
            return render(
                request=request,
                template_name='manage_store/upload_files_rslt.html',
                context={'links_file': links_file_obj},
            )
        else:
            return HttpResponse(content='Переданные данные не прошли валидацию', status=400)


def add_category_view(request):
    """
    Вьюшка для обработки добавления категории (папки)
    """
    # Редирект, если незалогинен
    if not request.user.is_superuser or not request.user.is_staff:
        return redirect(to=reverse_lazy('manage_store:login'))

    if request.method == 'POST':
        form = AddCategoryForm(request.POST)
        if form.is_valid():
            try:
                Category.objects.create(
                    cat_name=form.cleaned_data.get("cat_name")
                )
                logger.success(f'Успешное создание категории с cat_name == {form.cleaned_data.get("cat_name")}')
            except Exception as error:
                logger.warning(f'Ошибка при создании категории. Текст ошибки: {error}')
                return HttpResponse(status=400, content='Ошибка при записи данных')
            return redirect(reverse_lazy('manage_store:upload'))
        return HttpResponse(status=400, content='Данные, переданные в форму не прошли валидацию')
    else:
        return HttpResponse(status=400)


class MyLoginView(View):
    """
    Вьюшка для логина
    """

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse_lazy('manage_store:head_page'))

        return render(request, 'manage_store/login.html', context={
            'form': AuthenticationForm(),
        })

    def post(self, request):

        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request=request, username=username, password=password)  # вернёт None или объект User
        if user:
            login(request=request, user=user)
            return redirect(reverse_lazy('manage_store:head_page'))

        return render(request, "manage_store/login.html", context={
            "error": "Неверные логин или пароль",
            "form": AuthenticationForm(),
        })
