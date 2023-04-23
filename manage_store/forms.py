from django import forms

from manage_store.models import Category


class UploadProductFilesForm(forms.Form):
    """
    Форма для загрузки множества файлов - цифровых товаров.
    """
    category = forms.ChoiceField(
        choices=[],
        label='📂 Папка',
        required=True,
    )
    files = forms.FileField(
        label='🖱 Загрузить несколько файлов',
        widget=forms.ClearableFileInput(attrs={
            'multiple': True,
        }),
        required=True
    )

    def __init__(self, *args, **kwargs):
        """
        Переопределяем метод конструктора так,
        чтобы при создании инстанса класса формы в cat_list добавлялись значения из БД.
        """
        super().__init__(*args, **kwargs)
        # Создаём список категорий
        cat_list = [(i_cat.pk, i_cat.cat_name) for i_cat in Category.objects.all()]
        if cat_list:    # Если в БД уже созданы категории, то добавляем их
            self.fields['category'].choices = cat_list
        else:   # Иначе делаем заглушку
            self.fields['category'].choices = [(0, 'папки не созданы')]


class AddCategoryForm(forms.Form):
    """
    Форма для добавления категории (папки для Димана).
    """
    cat_name = forms.CharField(
        max_length=100,
        required=True,
        label='🆕📁 Добавить новую папку',
        widget=forms.TextInput(attrs={
            'placeholder': 'Имя папки',
        })
    )
