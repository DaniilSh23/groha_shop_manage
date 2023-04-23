from django.contrib import admin

from manage_store.models import ProductFiles, Category, ProjectSettings


@admin.register(ProductFiles)
class ProductFilesAdmin(admin.ModelAdmin):
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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
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
class ProjectSettings(admin.ModelAdmin):
    list_display = [
        'id',
        'key',
    ]
    list_display_links = [
        'id',
        'key',
    ]
