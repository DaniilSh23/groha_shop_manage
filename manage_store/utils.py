"""
Разные функции, которые выполняют какую-либо логику и служат как вспомогательный инструмент в основном коде.
"""
from urllib.parse import urlparse


def extract_domain(url):
    """
    Функция для извлечения домена из ссылки.
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain


def update_file_with_links_list(file_path, new_domain):
    """
    Функция для обновления файла со списком ссылок.
    """
    with open(file=file_path, mode='r', encoding='utf-8') as file:
        lines = file.readlines()
    with open(file=file_path, mode='w', encoding='utf-8') as new_file:
        for i_line in lines:
            old_domain = extract_domain(url=i_line.strip())
            new_file.write(f"{i_line.replace(old_domain, new_domain)}")
