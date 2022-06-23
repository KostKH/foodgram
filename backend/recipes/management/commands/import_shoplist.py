import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Recipe, ShopList
from users.models import User

DATA_ROOT = os.path.join(settings.BASE_DIR, 'data/')


class Command(BaseCommand):
    help = (
        'Загрузка рецептов в списке покупок в базу данных из csv-файла '
        f'поместите файл в папку {DATA_ROOT} и запустите команду:'
        'python manage.py import_shoplist filename=\'имя файла\''
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            default='shoplist.csv',
            nargs='?',
            type=str
        )

    def handle(self, *args, **options):
        input_file = options['filename']
        errors_in_data = []
        try:
            csv_file = open(os.path.join(DATA_ROOT, input_file),
                            newline='', encoding='utf8')
            file_content = csv.reader(csv_file)
            csv_file.close()
        except FileNotFoundError:
            raise CommandError(
                f'Файл {input_file} не найден в папке {DATA_ROOT}'
            )

        for row in file_content:
            recipe_id, username = row
            try:
                user = User.objects.get(username=username)
                recipe = Recipe.objects.get(id=recipe_id)
                ShopList.objects.create(
                    shopper=user,
                    recipe_to_shop=recipe
                )
            except Exception:
                errors_in_data.append(', '.join(row))

        if errors_in_data:
            output_file = os.path.join(DATA_ROOT, 'errors_shoplist.txt')
            output = '\n'.join(errors_in_data)
            with open(output_file, 'w') as file:
                file.write(output)
            print(
                'Были загружены не все данные. Список незагруженных строк '
                'приведен в файле:\n'
                f'{output_file}\n'
                'Проверьте данные по позициям в файле'
            )
        else:
            print(f'Данные из файла {input_file} успешно загружены')