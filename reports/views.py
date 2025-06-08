from django.shortcuts import render, get_object_or_404, redirect  # Добавьте redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils.safestring import mark_safe
from .models import ReportTemplate, DictionaryItem
from .forms import ReportForm
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


def generate_pdf_report(request, template_id):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method")

    template = get_object_or_404(ReportTemplate, id=template_id)
    template_fields = template.templatefield_set.all()

    form = ReportForm(request.POST, template_fields=template_fields)
    if not form.is_valid():
        return HttpResponseBadRequest("Invalid form data")

    try:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{template.name}.pdf"'

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)

        # Настройка PDF
        p.setTitle(template.name)
        p.setFont("Helvetica", 12)

        # Генерация содержимого
        report_content = template.generate_report(form.cleaned_data)
        text = p.beginText(40, 800)

        for line in report_content.split('\n'):
            text.textLine(line.strip())

        p.drawText(text)
        p.showPage()
        p.save()

        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)

        return response
    except Exception as e:
        messages.error(request, f"Ошибка при генерации PDF: {str(e)}")
        return redirect('reports:view_report', template_id=template_id)


def home_view(request):
    templates = ReportTemplate.objects.all()
    return render(request, 'reports/home.html', {'templates': templates})


def view_report(request, template_id):
    template = get_object_or_404(ReportTemplate, id=template_id)
    template_fields = template.templatefield_set.all()

    if request.method == 'POST':
        form = ReportForm(request.POST, template_fields=template_fields)
        if form.is_valid():
            # Сохраняем данные в сессии ДО перенаправления
            request.session['print_data'] = {
                'template_id': template_id,  # Обязательно сохраняем ID
                'form_data': form.cleaned_data
            }
            request.session.modified = True  # Принудительно сохраняем сессию

            if 'print' in request.POST:
                return redirect('reports:print_report', template_id=template_id)
            elif 'pdf' in request.POST:
                return generate_pdf_report(request, template_id)

            # Обычный просмотр отчета
            report_content = template.generate_report(form.cleaned_data)
            return render(request, 'reports/generated_report.html', {
                'template': template,
                'content': report_content
            })
    else:
        form = ReportForm(template_fields=template_fields)

    # Генерация предпросмотра формы
    content = template.content
    for field in template_fields:
        field_html = f'<span class="form-field">{form[field.placeholder]}</span>'
        content = content.replace(f'{{{{{field.placeholder}}}}}', field_html)

    return render(request, 'reports/view.html', {
        'content': content,
        'form': form,
        'template': template
    })

def report_view(request):
    template = ReportTemplate.objects.first()  # Берём первый шаблон
    text = template.content

    # Заменяем {{field_1}} на выпадающие списки

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


def print_report(request, template_id):
    template = get_object_or_404(ReportTemplate, id=template_id)

    # Достаем данные из сессии
    print_data = request.session.get('print_data', {})

    # Проверяем, что данные есть и template_id совпадает
    if not print_data or print_data.get('template_id') != template_id:
        return redirect('reports:view_report', template_id=template_id)

    # Генерируем отчет
    report_content = template.generate_report(print_data['form_data'])

    # Удаляем данные из сессии после использования (опционально)
    if 'print_data' in request.session:
        del request.session['print_data']

    return render(request, 'reports/print.html', {
        'template': template,
        'content': report_content
    })