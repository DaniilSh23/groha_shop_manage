from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from manage_store.views import DownloadProductFileView, UploadProductFilesView, MyLoginView, add_category_view

app_name = 'manage_store'

urlpatterns = [
    path('', UploadProductFilesView.as_view(), name='head_page'),   # TODO: сделать главную и подставить view
    path('login/', MyLoginView.as_view(), name='login'),
    path('dwnld/<str:file_hash>/', DownloadProductFileView.as_view(), name='dwnld'),
    path('upload/', UploadProductFilesView.as_view(), name='upload'),
    path('add_category/', add_category_view, name='add_category'),
]


if settings.DEBUG:  # Для обработки статики и медиа во время разработки
    urlpatterns.extend(
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )
    urlpatterns.extend(
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )
