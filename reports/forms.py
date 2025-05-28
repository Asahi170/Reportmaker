from django import forms
from .models import DictionaryItem

class ReportForm(forms.Form):
    def __init__(self, *args, **kwargs):
        template_fields = kwargs.pop('template_fields', [])
        super().__init__(*args, **kwargs)

        for field in template_fields:
            if field.field_type == 'select':
                choices = [(item.id, item.value) for item in field.dictionary.dictionaryitem_set.all()]
                self.fields[field.placeholder] = forms.ChoiceField(
                    choices=choices,
                    widget=forms.Select(attrs={'class': 'form-select inline-select'}),
                    label=field.label,
                    required=True
                )
            elif field.field_type == 'number':
                self.fields[field.placeholder] = forms.IntegerField(
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control inline-number',
                        'min': field.min_value,
                        'max': field.max_value
                    }),
                    label=field.label,
                    required=True
                )
            elif field.field_type == 'text':
                self.fields[field.placeholder] = forms.CharField(
                    widget=forms.TextInput(attrs={'class': 'form-control inline-text'}),
                    label=field.label,
                    required=True
                )

