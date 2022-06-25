from django.conf import settings
from django.http import HttpResponse


def convert_to_txt(shoplist):
    file_name = settings.SHOPLIST_FILE_NAME
    lines = []
    for item in shoplist:
        name = item['ingredient__name']
        measurement_unit = item['ingredient__measurement_unit']
        amount = item['ingredient_total']
        lines.append(f'{name} - {amount} {measurement_unit}')
    lines.append('\nПриятного аппетита! Ваш FoodGram')
    content = '\n'.join(lines)
    content_type = 'text/plain,charset=utf8'
    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    return response
