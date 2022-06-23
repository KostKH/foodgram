import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Tag
from recipes.serializers import TagSerializer

DATA_ROOT = os.path.join(settings.BASE_DIR, 'data/')


class Command(BaseCommand):
    help = (
        'Загрузка тегов в базу данных из csv-файла '
        f'поместите файл в папку {DATA_ROOT} и запустите команду:'
        'python manage.py import_tags filename=\'имя файла\''
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            default='tags.csv',
            nargs='?',
            type=str
        )

    def handle(self, *args, **options):
        input_file = options['filename']
        errors_in_data = []
        with open(
            os.path.join(DATA_ROOT, input_file),
            newline='',
            encoding='utf8'
        ) as csv_file:
            try:
                file_content = csv.reader(csv_file)
                for row in file_content:
                    tag_data = {
                        'slug': row[0],
                        'color': row[1],
                        'name': row[2],
                    }

                    serializer = TagSerializer(data=tag_data)
                    if serializer.is_valid():
                        Tag.objects.get_or_create(**tag_data)
                    else:
                        errors_in_data.append(', '.join(row))
            except FileNotFoundError:
                raise CommandError(
                    f'Файл {input_file} не найден в папке {DATA_ROOT}'
                )

        if errors_in_data:
            output_file = os.path.join(DATA_ROOT, 'errors_tags.txt')
            output = '\n'.join(errors_in_data)
            with open(output_file, 'w') as file:
                file.write(output)
            print(
                'Были загружены не все данные. Список незагруженных имен '
                'приведен в файле:\n'
                f'{output_file}\n'
                'Проверьте данные по позициям в файле'
            )
        else:
            print(f'Данные из файла {input_file} успешно загружены')
