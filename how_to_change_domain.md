# Как изменить домен на хосте

1. Подключаемся к хосту по ssh под пользователем root
2. Выполняем команду ```nano /etc/nginx/sites-available/manage_groha_store``` . Нам откроется на редактирование файл конфига NGINX
3. Редактируем конфиг NGINX, заменяем старый домен на новый. В конфиге указана подсказка где и что поменять. Там все просто.
4. Протестим NGINX, выполнив команду ```nginx -t```
    Должны будем увидеть в терминале две таких строки
    ```
    nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
    nginx: configuration file /etc/nginx/nginx.conf test is successful
    ```
5. Перезапустим всю хуйню, выполнив команду
    ```sudo systemctl restart nginx && sudo systemctl restart gunicorn && sudo systemctl restart celery```

6. Открываем в браузере сайт и проверяем, что все заебись работает.