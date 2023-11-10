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
