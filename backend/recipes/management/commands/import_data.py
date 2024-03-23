import json

from django.core.management.base import BaseCommand, CommandParser

from recipes.models import Ingredient, Tag


class Command(BaseCommand):

    help = 'Импорт данных из JSON-файлов'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('path', type=str, help='Пусть к JSON-файлу')

    def handle(self, *args, **options):
        path = options['path']
        if not Tag.objects.exists():
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if 'color' in data[0]:
                    for line in data:
                        Tag.objects.create(
                            name=line['name'],
                            color=line['color'],
                            slug=line['slug']
                        )
        if not Ingredient.objects.exists():
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if 'measurement_unit' in data[0]:
                    for line in data:
                        Ingredient.objects.create(
                            name=line['name'],
                            measurement_unit=line['measurement_unit']
                        )
