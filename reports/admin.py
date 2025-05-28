from django.contrib import admin
from .models import *

class DictionaryItemInline(admin.TabularInline):
    model = DictionaryItem
    extra = 1

@admin.register(Dictionary)
class DictionaryAdmin(admin.ModelAdmin):
    inlines = [DictionaryItemInline]

class TemplateFieldInline(admin.TabularInline):
    model = TemplateField
    extra = 1
    fields = ('placeholder', 'label', 'field_type', 'dictionary', 'min_value', 'max_value')

@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    inlines = [TemplateFieldInline]

