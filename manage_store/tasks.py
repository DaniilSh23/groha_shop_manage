import time
from loguru import logger
from celery import shared_task

from manage_store.models import ProductFiles


@shared_task
def hello_world_task():
    print('hello world from celery')


@shared_task
def deleting_obsolete_files():
    logger.info('Запуск задачи по расписанию для удаления устаревших файлов')

    for i_obj in ProductFiles.objects.filter(is_sold=True):     # Берём все проданные файлы
        if time.time() >= float(i_obj.time_for_delete):     # Если текущее время >= времени жизни файлов
            i_obj.delete()
            logger.info(f'Файл {i_obj.origin_file_name} категории {i_obj.category} удалён.')
    logger.success('Окончание задачи по удалению устаревших файлов')