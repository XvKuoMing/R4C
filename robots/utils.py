import re
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.cell import WriteOnlyCell


def generate_xlsx_response_from_objects(data, field_name, divide_by):
    """Takes query set <data> and prints it to excel, divides given field name by given keys and prins them
    on different pages """
    workbook = Workbook(write_only=True)
    bold = Font(bold=True)
    for page_key in divide_by:
        worksheet_data = data.filter(**{field_name: page_key})
        if not worksheet_data.exists():
            # уникальный ключей в датасете больше, чем после фильтрации, поэтому такие ключи мы просто пропускаем
            # в экселе это будет просто пустой sheet (убрать?)
            break
        worksheet = workbook.create_sheet(title=page_key)
        table_names = list(worksheet_data[0].keys())
        headers = []
        for cell_value in table_names:
            header_cell = WriteOnlyCell(worksheet, value=cell_value)
            header_cell.font = bold
            headers.append(header_cell)
        worksheet.append(headers)

        for object_as_row in worksheet_data:  # iterates through queryset
            worksheet.append(list(object_as_row.values()))

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=RobotsWeekCount.xlsx'
    workbook.save(response)
    return response


def re_validator(for_field):
    assert for_field in ['model', 'version'], f'валидатор RegexValidator не подходит под поле {for_field}'
    pat_str = r'''
                ^[A-Z]\d$     # строка типа D5, L3 (первая заглавная буква латиницы, вторая цифра)
                |^[A-Z]{2}$   # ИЛИ строка типа DD, LS, XX (ровно две заглавные буквы латиницы)
                |\d{2}        # ИЛИ строка типа 55, 11, 17 (ровно две цифры)
                '''
    pat = re.compile(pat_str, re.VERBOSE)
    return RegexValidator(pat,
                          message=_(f'Invalid {for_field} name'),
                          code=f'invalid_{for_field}')
