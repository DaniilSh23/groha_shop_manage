from django.core.management import BaseCommand

from manage_store.models import ProjectSettings


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Команда для установки настроек (создание инстансов модели ProjectSettings
        """
        self.stdout.write('Запуск команды по установке настроек')
        default_settings = (
            ('time_to_delete', 60*36),  # Время до удаления файлов, после скачивания клиентом
            ('admin_time_to_del', 120),    # Время до удаления файлов, после действия админа
        )
        for i_key, i_val in default_settings:
            setting_obj, created = ProjectSettings.objects.update_or_create(
                key=i_key,
                defaults={
                    'key': i_key,
                    'value': i_val,
                }
            )
            if created:
                self.stdout.write(f'Создана настройка ключ={setting_obj.key}, значение={setting_obj.value}')
            else:
                self.stdout.write(f'Обновлена настройка ключ={setting_obj.key}, значение={setting_obj.value}')
        self.stdout.write(self.style.SUCCESS('Установка настроек закончена!'))
