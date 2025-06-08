from django import forms
from .models import DictionaryItem


class ReportForm(forms.Form):
    def __init__(self, *args, **kwargs):
        template_fields = kwargs.pop('template_fields', [])
        super().__init__(*args, **kwargs)

        for field in template_fields:
            if field.field_type == 'select':
                if not field.dictionary:
                    raise ValueError(f"Для поля {field.placeholder} не выбран словарь")

                choices = [(item.id, item.value) for item in field.dictionary.dictionaryitem_set.all()]
                self.fields[field.placeholder] = forms.ChoiceField(
                    choices=choices,
                    widget=forms.Select(attrs={'class': 'form-select'}),
                    label=field.label,
                    required=True
                )
            elif field.field_type == 'number':
                self.fields[field.placeholder] = forms.IntegerField(
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control',
                        'min': field.min_value,
                        'max': field.max_value
                    }),
                    label=field.label,
                    required=True,
                    min_value=field.min_value,
                    max_value=field.max_value
                )
            elif field.field_type == 'text':
                self.fields[field.placeholder] = forms.CharField(
                    widget=forms.TextInput(attrs={'class': 'form-control'}),
                    label=field.label,
                    required=True
                )
            elif field.field_type == 'date':
                self.fields[field.placeholder] = forms.DateField(
                    widget=forms.DateInput(attrs={
                        'class': 'form-control datepicker',
                        'type': 'date'  # Это активирует встроенный календарь в современных браузерах
                    }),
                    label=field.label,
                    required=True
                )