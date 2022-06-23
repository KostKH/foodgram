import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Tag
from recipes.serializers import AddRecipeSerializer
from users.models import User

DATA_ROOT = os.path.join(settings.BASE_DIR, 'data/')


class Command(BaseCommand):
    help = (
        'Загрузка рецептов в базу данных из csv-файла '
        f'поместите файл в папку {DATA_ROOT} и запустите команду:'
        'python manage.py import_recipes filename=\'имя файла\''
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            default='recipes.csv',
            nargs='?',
            type=str
        )
        parser.add_argument(
            'imagestring',
            default='image.txt',
            nargs='?',
            type=str
        )

    def handle(self, *args, **options):
        errors_in_data = []
        input_file, image_file = options['filename'], options['imagestring']

        with open(os.path.join(DATA_ROOT, image_file), 'r') as image:
            image_read = image.read()

        with open(
            os.path.join(DATA_ROOT, input_file),
            newline='',
            encoding='utf8'
        ) as csv_file:
            file_content = csv.reader(csv_file)
            for row in file_content:
                recipe_tags = [number for number in row[11:14]]
                recipe_ingredients = [
                    {'id': int(row[5]), 'amount': int(row[6])},
                    {'id': int(row[7]), 'amount': int(row[8])},
                    {'id': int(row[9]), 'amount': int(row[10])}
                ]
                recipe_author = User.objects.get(username=row[1])

                recipe_data = {
                    'image': image_read,
                    'author': recipe_author,
                    'name': row[2],
                    'text': row[3],
                    'cooking_time': int(row[4]),
                    'tags': recipe_tags,
                    'ingredients': recipe_ingredients
                }
                recipe_tags = [
                    Tag.objects.get(id=number) for number in row[11:14]
                ]
                serializer = AddRecipeSerializer(data=recipe_data)
                if serializer.is_valid():
                    serializer.save(author=recipe_author)
                else:
                    errors_in_data.append(', '.join(row))

        if errors_in_data:
            output_file = os.path.join(DATA_ROOT, 'errors_recipe.txt')
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
