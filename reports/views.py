from django.shortcuts import render, get_object_or_404
from .models import ReportTemplate
from django.utils.safestring import mark_safe
import re
import os
from django.conf import settings
from .forms import ReportForm
from django.views.generic import TemplateView

def home_view(request):
    templates = ReportTemplate.objects.all()
    return render(request, 'reports/home.html', {'templates': templates})


def view_report(request, template_id):
    template = get_object_or_404(ReportTemplate, id=template_id)
    template_fields = template.templatefield_set.all()

    if request.method == 'POST':
        form = ReportForm(request.POST, template_fields=template_fields)
        if form.is_valid():
            report_content = template.generate_report(form.cleaned_data)
            return render(request, 'reports/generated_report.html', {
                'template': template,
                'content': mark_safe(report_content)
            })
    else:
        form = ReportForm(template_fields=template_fields)

    content = template.content
    for field in template_fields:
        field_html = f'<span class="form-field">{form[field.placeholder]}</span>'
        content = content.replace(f'{{{{{field.placeholder}}}}}', field_html)

    return render(request, 'reports/view.html', {
        'content': mark_safe(content),
        'form': form,
        'template': template
    })

print(os.path.join(settings.BASE_DIR, 'reports', 'templates', 'reports', 'report.html'))


def report_view(request):
    template = ReportTemplate.objects.first()  # Берём первый шаблон
    text = template.content

    # Заменяем {{field_1}} на выпадающие списки
    fields = {}
    for field in template.templatefield_set.all():
        choices = field.dictionary.dictionaryitem_set.all()
        select_html = f"""
        <select name="{field.placeholder}" class="form-select">
            {' '.join(
        f'<option value="{item.id}">{item.value}</option>' 
        for item in field.dictionary.dictionaryitem_set.all()
        )}
        </select>
        """
        text = text.replace(f"{{{{{field.placeholder}}}}}", select_html)

    return render(request, 'reports/report.html', {'text': mark_safe(text)})

def format_text(text):
    # Заменяем спецсимволы на HTML-аналоги
    return mark_safe(
        text.replace('\t', '&emsp;&emsp;')
           .replace('\n', '<br>')
           .replace('{{', '<input type="text" class="report-field">')
    )
