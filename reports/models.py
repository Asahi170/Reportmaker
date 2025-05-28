from django.db import models


class Dictionary(models.Model):
    """Справочники"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# Добавим стандартные справочники через миграцию
def create_default_dictionaries(apps, schema_editor):
    Dictionary = apps.get_model('reports', 'Dictionary')
    DictionaryItem = apps.get_model('reports', 'DictionaryItem')

    # Справочник должностей
    positions, _ = Dictionary.objects.get_or_create(name="Должности")
    for position in ['Инженер', 'Техник', 'Аналитик', 'Руководитель']:
        DictionaryItem.objects.get_or_create(dictionary=positions, value=position)

    # Справочник периодов контроля
    periods, _ = Dictionary.objects.get_or_create(name="Периоды контроля")
    for period in ['Ежедневно', 'Еженедельно', 'Ежемесячно', 'Ежеквартально']:
        DictionaryItem.objects.get_or_create(dictionary=periods, value=period)


class DictionaryItem(models.Model):
    """Элементы справочника (например, "Иванов И.И.")"""
    dictionary = models.ForeignKey(Dictionary, on_delete=models.CASCADE)
    value = models.CharField(max_length=200)

    def __str__(self):
        return self.value


class ReportTemplate(models.Model):
    name = models.CharField(max_length=200)
    content = models.TextField(
        help_text="Используйте {{field}} для полей. Пример:\n"
                "Отчет подготовил: {{employee}}\n"
                "Дата: {{date}}"
    )
    def save(self, *args, **kwargs):
        # Автоматически заменяем \n на настоящие переносы
        self.content = self.content.replace('\\n', '\n')
        super().save(*args, **kwargs)

    def generate_report(self, form_data):
        content = self.content
        for field in self.templatefield_set.all():
            if field.field_type == 'select':
                item = DictionaryItem.objects.get(
                    id=form_data[field.placeholder],
                    dictionary=field.dictionary
                )
                content = content.replace(f'{{{{{field.placeholder}}}}}', item.value)
            else:
                # Для числовых и текстовых полей просто подставляем значение
                content = content.replace(f'{{{{{field.placeholder}}}}}', str(form_data[field.placeholder]))
        return content


class TemplateField(models.Model):
    FIELD_TYPES = [
        ('select', 'Выпадающий список'),
        ('number', 'Числовое поле'),
        ('text', 'Текстовое поле'),
    ]

    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE)
    placeholder = models.CharField(max_length=50, help_text="Название для вставки (например: field_1)")
    label = models.CharField(max_length=100, help_text="Подпись поля (например: 'ФИО сотрудника')")
    dictionary = models.ForeignKey(Dictionary, on_delete=models.CASCADE, null=True, blank=True,
                                   help_text="Откуда брать варианты (только для выпадающего списка)")
    field_type = models.CharField(max_length=10, choices=FIELD_TYPES, default='select',
                                  help_text="Тип поля для ввода")
    min_value = models.IntegerField(null=True, blank=True, help_text="Минимальное значение (для числовых полей)")
    max_value = models.IntegerField(null=True, blank=True, help_text="Максимальное значение (для числовых полей)")

    def __str__(self):
        return f"{self.label} ({{{{{self.placeholder}}}}})"

